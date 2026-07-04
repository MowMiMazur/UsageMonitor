import time
import threading
import psutil
from statistics import mean

from core.constants import APP_NAME, get_full_version, AUTHOR_NAME, AUTHOR_URL


class Monitor:
    """Samples a process's CPU/RAM usage on a background thread.

    Reports through callbacks: on_sample(dict), on_finished(report), on_error(str).
    """

    def __init__(self, pid, proc_name="proces", interval=1.0):
        self.pid = pid
        self.proc_name = proc_name
        self.interval = float(interval)

        self.on_sample = None
        self.on_finished = None
        self.on_error = None

        self._stop = threading.Event()
        self._thread = None

        self.cpu_count = psutil.cpu_count(logical=True) or 1
        self.series = {"t": [], "cpu_raw": [], "cpu_norm": [], "ram": []}
        self.start_time = None
        self.end_time = None

    def start(self):
        self._thread = threading.Thread(target=self._run, name="usagemonitor", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        try:
            proc = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            self._safe(self.on_error, {"code": "process_missing", "pid": self.pid})
            return

        self.start_time = time.time()

        try:
            proc.cpu_percent(interval=None)  # prime the CPU counter (first read is always 0)

            while not self._stop.is_set():
                if self._stop.wait(self.interval):  # sleep, but return immediately on stop
                    break
                if not proc.is_running():
                    break

                try:
                    cpu_raw = proc.cpu_percent(interval=None)
                    cpu_norm = cpu_raw / self.cpu_count
                    ram = proc.memory_info().rss / (1024 * 1024)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

                t = time.strftime("%H:%M:%S")
                self.series["t"].append(t)
                self.series["cpu_raw"].append(round(cpu_raw, 2))
                self.series["cpu_norm"].append(round(cpu_norm, 2))
                self.series["ram"].append(round(ram, 2))

                self._safe(self.on_sample, {
                    "t": t,
                    "cpu_raw": round(cpu_raw, 2),
                    "cpu_norm": round(cpu_norm, 2),
                    "ram": round(ram, 2),
                })
        except Exception as e:
            self._safe(self.on_error, {"code": "generic", "detail": str(e)})
            return

        self.end_time = time.time()
        self._safe(self.on_finished, self.build_report())

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
            },
            "series": self.series,
        }

    @staticmethod
    def _safe(cb, arg):
        if cb:
            try:
                cb(arg)
            except Exception:
                pass
