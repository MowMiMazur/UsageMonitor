import time
import threading
import psutil
from statistics import mean

from core.group import ProcessGroup, snapshot
from core.constants import APP_NAME, get_full_version, AUTHOR_NAME, AUTHOR_URL

# Per-process rows kept in the report; the rest is folded into one "others" row
# so a long session full of short-lived tabs cannot bloat the exported HTML.
MAX_PROCESS_ROWS = 60


class _Tracked:
    """One process being sampled, plus the totals it has accumulated."""

    __slots__ = ("proc", "pid", "name", "created", "samples",
                 "cpu_sum", "cpu_max", "ram_sum", "ram_max")

    def __init__(self, proc, name, created):
        self.proc = proc
        self.pid = proc.pid
        self.name = name
        self.created = created
        self.samples = 0
        self.cpu_sum = 0.0
        self.cpu_max = 0.0
        self.ram_sum = 0.0
        self.ram_max = 0.0

    def add(self, cpu, ram):
        self.samples += 1
        self.cpu_sum += cpu
        self.ram_sum += ram
        if cpu > self.cpu_max:
            self.cpu_max = cpu
        if ram > self.ram_max:
            self.ram_max = ram


class Monitor:
    """Samples the CPU/RAM usage of a target on a background thread.

    The target is a ProcessGroup, so a session covers either one PID or a whole
    family of them (all firefox.exe, a process tree, a hand-picked set). Group
    membership is re-resolved every tick, and the reported series are the sums
    across whatever belonged at that moment.

    Reports through callbacks: on_sample(dict), on_finished(report), on_error(dict).
    """

    def __init__(self, group, proc_name="proces", interval=1.0):
        self.group = group if isinstance(group, ProcessGroup) else ProcessGroup.from_spec(group)
        self.pid = self.group.pid
        self.proc_name = proc_name
        self.interval = float(interval)

        self.on_sample = None
        self.on_finished = None
        self.on_error = None

        self._stop = threading.Event()
        self._thread = None

        self.cpu_count = psutil.cpu_count(logical=True) or 1
        self.series = {"t": [], "cpu_raw": [], "cpu_norm": [], "ram": [], "procs": []}
        self.start_time = None
        self.end_time = None

        self._tracked = {}       # pid -> _Tracked, live members only
        self._history = {}       # (pid, created) -> _Tracked, every member ever seen
        self._peak_procs = 0

    def start(self):
        self._thread = threading.Thread(target=self._run, name="usagemonitor", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    # --- membership ---

    def _sync_members(self):
        """Bring self._tracked in line with the group's current membership."""
        rows = snapshot() if self.group.needs_scan else None
        wanted = self.group.resolve(rows)
        names = {pid: name for pid, _ppid, name in (rows or [])}

        for pid in list(self._tracked):
            if pid not in wanted:
                del self._tracked[pid]

        for pid in wanted:
            if pid in self._tracked:
                continue
            try:
                proc = psutil.Process(pid)
                created = proc.create_time()
                name = names.get(pid) or proc.name()
                proc.cpu_percent(interval=None)  # prime; this member scores 0 for one tick
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            key = (pid, round(created, 3))
            entry = self._history.get(key)
            if entry is None:
                entry = _Tracked(proc, name, created)
                self._history[key] = entry
            else:
                entry.proc = proc  # the same process rejoining the group
            self._tracked[pid] = entry

        return len(self._tracked)

    # --- sampling loop ---

    def _run(self):
        try:
            if not self._sync_members():
                self._safe(self.on_error, {"code": "process_missing", "pid": self.pid})
                return
        except Exception as e:
            self._safe(self.on_error, {"code": "generic", "detail": str(e)})
            return

        self.start_time = time.time()

        try:
            while not self._stop.is_set():
                if self._stop.wait(self.interval):  # sleep, but return immediately on stop
                    break
                if not self._sync_members():
                    break  # the whole group is gone: a normal end of session

                cpu_raw = 0.0
                ram = 0.0
                counted = 0
                for entry in list(self._tracked.values()):
                    try:
                        c = entry.proc.cpu_percent(interval=None)
                        r = entry.proc.memory_info().rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self._tracked.pop(entry.pid, None)
                        continue
                    entry.add(c, r)
                    cpu_raw += c
                    ram += r
                    counted += 1

                if not counted:
                    break

                cpu_norm = cpu_raw / self.cpu_count
                if counted > self._peak_procs:
                    self._peak_procs = counted

                t = time.strftime("%H:%M:%S")
                sample = {
                    "t": t,
                    "cpu_raw": round(cpu_raw, 2),
                    "cpu_norm": round(cpu_norm, 2),
                    "ram": round(ram, 2),
                    "procs": counted,
                }
                for key, value in sample.items():
                    self.series[key].append(value)
                self._safe(self.on_sample, sample)
        except Exception as e:
            self._safe(self.on_error, {"code": "generic", "detail": str(e)})
            return

        self.end_time = time.time()
        self._safe(self.on_finished, self.build_report())

    # --- report ---

    def _per_process(self):
        """Breakdown rows, biggest CPU consumer first, tail folded into one row."""
        entries = [e for e in self._history.values() if e.samples]
        if not entries:
            return []
        total_cpu = sum(e.cpu_sum for e in entries) or 1.0
        entries.sort(key=lambda e: e.cpu_sum, reverse=True)

        def row(e):
            return {
                "pid": e.pid,
                "name": e.name,
                "samples": e.samples,
                "cpu_avg": round(e.cpu_sum / e.samples, 2),
                "cpu_max": round(e.cpu_max, 2),
                "ram_avg": round(e.ram_sum / e.samples, 2),
                "ram_max": round(e.ram_max, 2),
                "cpu_share": round(e.cpu_sum / total_cpu * 100.0, 1),
            }

        rows = [row(e) for e in entries[:MAX_PROCESS_ROWS]]
        rest = entries[MAX_PROCESS_ROWS:]
        if rest:
            samples = sum(e.samples for e in rest)
            rows.append({
                "pid": None,
                "name": None,
                "is_others": True,
                "others_count": len(rest),
                "samples": samples,
                "cpu_avg": round(sum(e.cpu_sum for e in rest) / samples, 2) if samples else 0.0,
                "cpu_max": round(max(e.cpu_max for e in rest), 2),
                "ram_avg": round(sum(e.ram_sum for e in rest) / samples, 2) if samples else 0.0,
                "ram_max": round(max(e.ram_max for e in rest), 2),
                "cpu_share": round(sum(e.cpu_sum for e in rest) / total_cpu * 100.0, 1),
            })
        return rows

    def build_report(self):
        def stat(values):
            if not values:
                return {"min": 0.0, "max": 0.0, "avg": 0.0}
            return {"min": round(min(values), 2), "max": round(max(values), 2), "avg": round(mean(values), 2)}

        has_data = len(self.series["t"]) > 0

        start_ts = self.start_time or time.time()
        end_ts = self.end_time or time.time()
        duration = max(0, int(end_ts - start_ts))
        h, rem = divmod(duration, 3600)
        m, s = divmod(rem, 60)
        duration_str = (f"{h}h {m}m {s}s" if h else (f"{m}m {s}s" if m else f"{s}s"))

        procs_series = self.series["procs"]
        return {
            "has_data": has_data,
            "meta": {
                "app": APP_NAME,
                "version": get_full_version(),
                "pid": self.pid,
                "proc_name": self.proc_name,
                "cpu_count": self.cpu_count,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "author_name": AUTHOR_NAME,
                "author_url": AUTHOR_URL,
                "output_file": "",
                "group": {
                    "is_group": self.group.is_group,
                    "mode": self.group.mode,
                    "label": self.proc_name,
                    "peak": self._peak_procs,
                    "last": procs_series[-1] if procs_series else 0,
                    "total_seen": len([e for e in self._history.values() if e.samples]),
                },
            },
            "session": {
                "start": time.strftime("%H:%M:%S", time.localtime(start_ts)),
                "end": time.strftime("%H:%M:%S", time.localtime(end_ts)),
                "duration_str": duration_str,
                "duration_seconds": duration,
                "samples": len(self.series["t"]),
                "interval": self.interval,
            },
            "stats": {
                "cpu_raw": stat(self.series["cpu_raw"]),
                "cpu_norm": stat(self.series["cpu_norm"]),
                "ram": stat(self.series["ram"]),
                "procs": stat(procs_series),
            },
            "series": self.series,
            "per_process": self._per_process(),
        }

    @staticmethod
    def _safe(cb, arg):
        if cb:
            try:
                cb(arg)
            except Exception:
                pass
