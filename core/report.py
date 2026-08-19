import os
import json
import time
import html

from core.utils import resource_path, app_base_dir
from core.constants import APP_NAME


def _read_web(name):
    """Read a bundled web asset by its path relative to web/ (e.g. "css/theme.css")."""
    with open(resource_path(os.path.join("web", *name.split("/"))), "r", encoding="utf-8") as f:
        return f.read()


# Extra page layout (css/app.css is not loaded in the standalone file).
_PAGE_STYLE = """
  .page { max-width: 880px; margin: 0 auto; padding: 34px 26px 56px; }
  .rep-header { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
  .rep-header .mark {
    width: 34px; height: 34px; border-radius: 10px;
    background: linear-gradient(145deg, var(--accent), var(--accent-2));
    display: grid; place-items: center;
    box-shadow: 0 4px 14px rgba(33,194,129,0.28), inset 0 1px 0 rgba(255,255,255,0.25);
  }
  .rep-header .mark svg { width: 19px; height: 19px; }
  .rep-header .t h1 { font-size: 20px; letter-spacing: -0.01em; }
  .rep-header .t .sub { color: var(--muted); font-size: 12.5px; margin-top: 2px; }
  .rep-header .rep-lang { margin-left: auto; }
  .rep-title-row { margin: 26px 0 18px; display: flex; align-items: baseline; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .rep-title-row h2 { font-size: 25px; letter-spacing: -0.02em; }
  .rep-title-row h2 .pid { font-family: var(--mono); font-size: 15px; color: var(--text-2); margin-left: 8px; }
  .rep-title-row .gen { color: var(--muted); font-size: 12px; font-family: var(--mono); }
  .rep-meta-line { color: var(--text-2); font-size: 13px; margin-top: 4px; }
  .rep-foot { display: block; margin-top: 34px; text-align: center; color: var(--muted); font-size: 12px; }
  .rep-foot a { color: var(--text-2); text-decoration: none; }
  .rep-foot .v { font-family: var(--mono); }
"""

_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}" class="theme-auto">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>
{theme_css}
{page_style}
</style>
</head>
<body>
<div class="page">
  <div id="report-header"></div>
  <div id="report-root" style="margin-top:22px"></div>
  <footer class="rep-foot" id="report-foot"></footer>
</div>

<script>
{i18n_js}
</script>
<script>
{charts_js}
</script>
<script>
{report_js}
</script>
<script>
  UMi18n.init({lang_json});
  window.__UM_REPORT__ = {data_json};
  UMReport.mountStandalone(window.__UM_REPORT__);
</script>
</body>
</html>
"""


def write_html_log(report, logs_dir=None, lang="pl"):
    """Write a self-contained, bilingual HTML report (log + summary + charts). Returns its path."""
    if logs_dir is None:
        logs_dir = os.path.join(app_base_dir(), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    meta = report.get("meta", {})
    pid = meta.get("pid", 0)
    proc_name = meta.get("proc_name", "process")

    safe_name = "".join(c for c in proc_name if c.isalnum() or c in (" ", ".", "_", "-")).strip()
    safe_name = safe_name.replace(" ", "_") or "process"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(logs_dir, f"{stamp}_{pid}-{safe_name}_usagemonitor.html")

    document = _TEMPLATE.format(
        lang=html.escape(lang),
        lang_json=json.dumps(lang),
        title=f"{APP_NAME} — {html.escape(proc_name)} (PID {pid})",
        theme_css=_read_web("css/theme.css"),
        page_style=_PAGE_STYLE,
        i18n_js=_read_web("js/i18n.js"),
        charts_js=_read_web("js/charts.js"),
        report_js=_read_web("js/report.js"),
        data_json=json.dumps(report, ensure_ascii=False),
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(document)

    report.setdefault("meta", {})["output_file"] = out_path
    return out_path
