"""Resolves which processes belong to a monitored target, tick by tick.

A target is one of four modes:

    single  one PID, the classic behaviour
    name    every process sharing a name (Firefox spawns a dozen firefox.exe)
    tree    an anchor PID plus everything descending from it
    set     an explicit list of PIDs picked by hand

`name` and `tree` are live: membership is recomputed on every sample, so
processes that appear or exit mid-session are followed. `tree` also keeps
members whose parent has already died - Windows reparents orphans, and losing
the children of a closed launcher would silently shrink the measurement.
"""

import psutil

MODES = ("single", "name", "tree", "set")

# Modes that must walk the whole process table on every sample.
_SCANNING_MODES = ("name", "tree")


def snapshot():
    """One pass over the process table -> [(pid, ppid, name), ...]."""
    rows = []
    for proc in psutil.process_iter(["pid", "ppid", "name"]):
        try:
            info = proc.info
            rows.append((info["pid"], info["ppid"], info["name"] or "?"))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return rows


class ProcessGroup:
    """Turns a target spec into the set of PIDs that currently belong to it."""

    def __init__(self, mode="single", pid=None, name=None, pids=None):
        if mode not in MODES:
            mode = "single"
        self.mode = mode
        self.pid = int(pid) if pid is not None else None
        self.name = (name or "").strip()
        self.pids = sorted({int(p) for p in (pids or [])})
        # tree mode remembers who it has seen, so orphaned children stay in scope
        self._known = {self.pid} if (mode == "tree" and self.pid is not None) else set()

    # --- construction ---

    @classmethod
    def from_spec(cls, spec):
        """Build from the dict the UI sends over the pywebview bridge."""
        if not isinstance(spec, dict):
            spec = {"mode": "single", "pid": spec}
        return cls(
            mode=spec.get("mode", "single"),
            pid=spec.get("pid"),
            name=spec.get("name"),
            pids=spec.get("pids"),
        )

    @property
    def needs_scan(self):
        return self.mode in _SCANNING_MODES

    @property
    def is_group(self):
        return self.mode != "single"

    # --- resolution ---

    def resolve(self, rows=None):
        """Return the set of PIDs belonging to the target right now.

        `rows` is the output of snapshot(); required for the scanning modes and
        ignored otherwise, so a single-PID session never pays for a full scan.
        """
        if self.mode == "single":
            return {self.pid} if self.pid is not None and psutil.pid_exists(self.pid) else set()

        if self.mode == "set":
            return {p for p in self.pids if psutil.pid_exists(p)}

        rows = rows if rows is not None else snapshot()

        if self.mode == "name":
            wanted = self.name.lower()
            return {pid for pid, _ppid, name in rows if name.lower() == wanted}

        # tree: closure of children over every member still alive
        alive = {pid for pid, _ppid, _name in rows}
        children = {}
        for pid, ppid, _name in rows:
            children.setdefault(ppid, []).append(pid)

        seeds = {p for p in self._known if p in alive}
        if self.pid in alive:
            seeds.add(self.pid)

        found, stack = set(seeds), list(seeds)
        while stack:
            for child in children.get(stack.pop(), ()):
                if child not in found:
                    found.add(child)
                    stack.append(child)

        self._known = found
        return found

    # --- description ---

    def describe(self, rows=None):
        """Label + member preview for the UI, without starting a session."""
        rows = rows if (rows is not None or not self.needs_scan) else snapshot()
        pids = self.resolve(rows)
        by_pid = {pid: name for pid, _ppid, name in (rows or [])}

        members = []
        for pid in sorted(pids):
            name = by_pid.get(pid)
            if name is None:
                try:
                    name = psutil.Process(pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    name = "?"
            members.append({"pid": pid, "name": name})

        return {
            "mode": self.mode,
            "label": self._label(members),
            "count": len(members),
            "members": members,
        }

    def _label(self, members):
        if self.name:
            return self.name
        if self.pid is not None:
            for m in members:
                if m["pid"] == self.pid:
                    return m["name"]
        if members:
            # the set mode has no anchor: name it after the most common member
            counts = {}
            for m in members:
                counts[m["name"]] = counts.get(m["name"], 0) + 1
            return max(counts, key=counts.get)
        return ""
