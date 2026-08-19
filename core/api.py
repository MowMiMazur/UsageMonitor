import os
import json
import threading
import webbrowser
import subprocess

import psutil

from core import updates
from core.monitor import Monitor
from core.report import write_html_log
from core.utils import get_process_list, app_base_dir
from core.constants import get_full_version, VERSION, AUTHOR_NAME, AUTHOR_URL


class Api:
    """JS <-> Python bridge exposed to the webview as js_api."""

    def __init__(self):
        self._window = None
        self._monitor = None
        self._lang = "pl"
        self._update_thread = None

    def set_window(self, window):
        self._window = window

    def set_lang(self, lang):
        if lang in ("pl", "en"):
            self._lang = lang

    def get_app_info(self):
        return {
            "version": get_full_version(),
            "version_number": VERSION,
            "author_name": AUTHOR_NAME,
            "author_url": AUTHOR_URL,
        }

    def start_update_check(self, force=False):
        """Kick off the version check off-thread; the result arrives via UM.onUpdate."""
        if self._update_thread and self._update_thread.is_alive():
            return {"ok": True, "pending": True}
        thread = threading.Thread(target=self._run_update_check, args=(bool(force),), daemon=True)
        self._update_thread = thread
        thread.start()
        return {"ok": True, "pending": True}

    def _run_update_check(self, force):
        try:
            result = updates.check(force=force)
        except Exception as e:  # the check must never take the app down
            result = {"ok": False, "error": "network", "detail": str(e)}
        self._js(f"window.UM && UM.onUpdate({json.dumps(result, ensure_ascii=False)});")

    def get_process_list(self):
        return [{"pid": pid, "name": name} for pid, name in get_process_list()]

    def start_monitoring(self, pid):
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            return {"ok": False, "error_key": "invalid_pid"}

        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except psutil.NoSuchProcess:
            return {"ok": False, "error_key": "process_missing", "pid": pid}
        except psutil.AccessDenied:
            proc_name = "process"

        monitor = Monitor(pid, proc_name=proc_name)
        monitor.on_sample = self._on_sample
        monitor.on_finished = self._on_finished
        monitor.on_error = self._on_error
        self._monitor = monitor
        monitor.start()

        return {
            "ok": True,
            "pid": pid,
            "proc_name": proc_name,
            "cpu_count": monitor.cpu_count,
        }

    def request_stop(self):
        if self._monitor:
            self._monitor.stop()

    def open_path(self, path):
        try:
            os.startfile(path)  # Windows
        except Exception:
            webbrowser.open("file://" + str(path))

    def reveal_path(self, path):
        try:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(str(path))])
        except Exception:
            try:
                os.startfile(os.path.dirname(str(path)))
            except Exception:
                pass

    def open_url(self, url):
        webbrowser.open(url)

    # --- Monitor callbacks -> JS ---

    def _js(self, code):
        if self._window is not None:
            try:
                self._window.evaluate_js(code)
            except Exception:
                pass

    def _on_sample(self, sample):
        self._js(f"window.UM && UM.onSample({json.dumps(sample, ensure_ascii=False)});")

    def _on_finished(self, report):
        if report.get("has_data"):
            try:
                write_html_log(report, os.path.join(app_base_dir(), "logs"), self._lang)
            except Exception as e:
                report.setdefault("meta", {})["output_file"] = ""
                print(f"[UsageMonitor] Failed to write HTML report: {e}")
        self._monitor = None
        self._js(f"window.UM && UM.onFinished({json.dumps(report, ensure_ascii=False)});")

    def _on_error(self, message):
        self._monitor = None
        self._js(f"window.UM && UM.onError({json.dumps(message, ensure_ascii=False)});")
