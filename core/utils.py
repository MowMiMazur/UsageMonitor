import os
import sys
import psutil


def resource_path(relative_path):
    """Resolve a bundled resource path, both from source and from a PyInstaller build."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def app_base_dir():
    """Directory next to the running program (where logs are written)."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_process_list():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name'] or "?"
            processes.append((proc.info['pid'], name))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(processes, key=lambda x: x[1].lower())
