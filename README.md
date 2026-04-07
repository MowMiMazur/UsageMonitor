# UsageMonitor

Monitor zużycia CPU/RAM dla wskazanego procesu.

> Copyright © 2026 MAZNET (Mateusz Mazur)

## Wymagania

- Python 3.11.9 (zalecany)
- PySide6
- psutil

## Instalacja

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python main.py
```

## Struktura projektu

```
UsageMonitor/
├── main.py
├── assets/
│   ├── icon.png
│   └── icon.ico
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── monitor.py
│   └── utils.py
├── theme/
│   ├── theme.py
│   └── global_qss.py
└── ui/
    ├── __init__.py
    ├── main_window.py
    ├── charts.py
    └── dialogs.py
```

## Kompilacja (PyInstaller)

```bash
pyinstaller --onefile --windowed --noconsole --noupx \
    --name UsageMonitor \
    --icon assets/icon.ico \
    --add-data "assets/icon.ico;assets" \
    --version-file version.txt \
    --clean --noconfirm main.py
```
