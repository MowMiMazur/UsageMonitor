# UsageMonitor

> Real-time CPU & RAM usage monitor for any selected process — built with Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-green?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-lightblue?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-Proprietary-lightgrey)
![Author](https://img.shields.io/badge/author-MAZNET-orange)

---

## Features

- **Process selection** — pick any running process from a filterable list
- **Live monitoring** — real-time CPU and RAM usage with elapsed-time counter
- **Interactive charts** — visualise CPU/RAM history after a monitoring session
- **Session summary** — min/max/average statistics shown when monitoring stops
- **Log export** — session data saved automatically to the `logs/` folder as `.log` files
- **CSV export** — export collected samples with a statistical summary
- **Dark UI** — custom dark theme built with PySide6 / Qt stylesheets

---

## Requirements

| Dependency | Version |
|------------|---------|
| Python     | 3.11+   |
| PySide6    | latest  |
| psutil     | latest  |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/maznet/UsageMonitor.git
cd UsageMonitor
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

1. Click **"Wybierz proces"** and pick a process from the list.
2. Click **"Start"** to begin monitoring.
3. Click **"Stop"** to end the session — a summary and charts will be available.
4. Log files are saved in the `logs/` folder automatically.

---

## Project Structure

```
UsageMonitor/
├── main.py               # Entry point
├── requirements.txt
├── version.txt           # PyInstaller version metadata
├── build.ps1             # PowerShell build script
├── assets/
│   ├── icon.png
│   └── icon.ico
├── core/
│   ├── constants.py      # App-wide constants
│   ├── monitor.py        # Monitoring logic (background thread)
│   └── utils.py          # Helper utilities
├── theme/
│   ├── theme.py          # Theme configuration
│   └── global_qss.py     # Qt stylesheet
├── ui/
│   ├── main_window.py    # Main application window
│   ├── charts.py         # Charts dialog
│   └── dialogs.py        # Process selection & summary dialogs
└── logs/                 # Auto-created; stores session log files
```

---

## Building an Executable (.exe)

The included `build.ps1` script handles everything automatically:

```powershell
.\build.ps1
```

The script will:
1. Auto-detect the Python interpreter
2. Ask for a version number (updates `version.txt` automatically)
3. Install `requirements.txt` and `PyInstaller`
4. Compile a single-file Windows executable
5. Move the result to `exec/UsageMonitor-{version}.exe`
6. Clean up temporary build files

> **Note:** If PowerShell blocks script execution, run once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## License

This project is proprietary software.  
© 2026 [MAZNET (Mateusz Mazur)](https://maznet.pl) — All rights reserved.

---

## Author

**MAZNET** — Mateusz Mazur  
🌐 [maznet.pl](https://maznet.pl)  
📧 mateusz@maznet.pl