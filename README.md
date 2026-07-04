<div align="center">

# UsageMonitor

**Real-time CPU & RAM monitor for any process** — a small Python core with a fully web-based (HTML/CSS/JS) interface rendered in a native window.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-pywebview%20%2F%20WebView2-2ea043?logo=googlechrome&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-Apache--2.0-brightgreen)

</div>

---

## Overview

Point UsageMonitor at a running process (by PID or picked from a list) and watch its CPU and RAM usage
live. When you stop, you get a clean report with charts — and every session is also saved as a
**self-contained HTML file** you can open in any browser, offline, showing the full sample log together
with the same summary and charts.

No Qt, no bundled Chromium: the UI is plain HTML/CSS/JS rendered through the OS **Edge WebView2** runtime.
The chart engine and report renderer are shared verbatim between the live app and the exported files.

## Features

- **Bilingual** — Polish / English, switchable at runtime; the exported report ships with its own toggle
- **Pick any process** — searchable list, or type a PID directly
- **Live monitoring** — real-time CPU (per-core & total) and RAM charts with an elapsed timer
- **Interactive charts** — custom SVG line charts with crosshair + tooltip, theme-aware
- **Polished report** — summary tiles (min / avg / max) and charts on stop
- **HTML export** — each session saved to `logs/` as a standalone `.html`: full log **+** summary **+** charts, light/dark aware, works offline
- **Zero web dependencies** — everything is inlined; nothing is fetched at runtime

## Requirements

| Dependency | Version |
|------------|---------|
| Python     | 3.11+   |
| pywebview  | latest  |
| psutil     | latest  |

> On Windows, pywebview uses the **Edge WebView2** runtime, preinstalled on Windows 10/11.

## Getting started

```bash
git clone https://github.com/maznet/UsageMonitor.git
cd UsageMonitor
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

1. Click **Wybierz program** and pick a process (or type a PID).
2. Click **Rozpocznij monitoring** — live charts and a timer appear.
3. Click **Zatrzymaj monitoring** — the report is shown.
4. Open the exported **HTML report** from the app, or find it in `logs/`.

## Project structure

```
UsageMonitor/
├── main.py               # Entry point — creates the pywebview window
├── requirements.txt
├── version.txt           # PyInstaller version metadata
├── build.ps1             # One-command Windows build script
├── assets/               # App icon
├── core/
│   ├── api.py            # JS <-> Python bridge (js_api)
│   ├── monitor.py        # Sampling loop (background thread, no GUI deps)
│   ├── report.py         # Builds the self-contained HTML report
│   ├── constants.py
│   └── utils.py          # Resource paths & process list
└── web/                  # The entire user interface
    ├── index.html        # App shell (single page)
    ├── theme.css         # Shared design system (app + report)
    ├── app.css / app.js  # App-shell styles & logic
    ├── charts.js         # Shared SVG chart engine
    └── report.js         # Shared report/summary renderer
```

`web/charts.js` and `web/report.js` are shared: the same code renders charts in the live app, in the
in-app report, and inside every exported HTML file.

## Building an executable

```powershell
.\build.ps1
```

Auto-detects Python, asks for a version, installs dependencies + PyInstaller, compiles a single-file
Windows executable (bundling `web/` and the pywebview backend), and writes it to
`exec/UsageMonitor-{version}.exe`.

> If PowerShell blocks script execution, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## License

Released under the **Apache License 2.0** — free to use, modify, and distribute, including in commercial
projects. In return you must **preserve attribution**: keep the copyright and authorship notices and
include the [NOTICE](NOTICE) file (crediting Mateusz Mazur / MAZNET as the author) with any copy or
derivative work, and state any changes you make. See [LICENSE](LICENSE).

## Author

**Mateusz Mazur** (MAZNET) · [maznet.pl](https://maznet.pl)
