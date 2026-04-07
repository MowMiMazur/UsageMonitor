# 🧠 UsageMonitor

> Monitor zużycia CPU i RAM dla wybranego procesu w czasie rzeczywistym

![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/license-MAZNET-lightgrey)

---

## ✨ Funkcje

* 📊 Monitorowanie CPU i RAM dla wybranego procesu
* ⏱️ Licznik czasu trwania monitorowania
* 📈 Wykresy zużycia zasobów w czasie
* 📄 Generowanie raportów
* 📤 Eksport danych do CSV (z podsumowaniem statystycznym)

---

## 📦 Wymagania

* Python 3.11.9 (zalecany)
* PySide6
* psutil

---

## 🚀 Instalacja

```bash
pip install -r requirements.txt
```

---

## ▶️ Uruchomienie

```bash
python main.py
```

---

## 🗂️ Struktura projektu

```
UsageMonitor/
├── main.py
├── assets/
│   ├── icon.png
│   └── icon.ico
├── core/
│   ├── constants.py
│   ├── monitor.py
│   └── utils.py
├── theme/
│   ├── theme.py
│   └── global_qss.py
└── ui/
    ├── main_window.py
    ├── charts.py
    └── dialogs.py
```

---

## 🏗️ Budowanie (.exe)

```bash
pyinstaller --onefile --windowed --noconsole --noupx \
    --name UsageMonitor \
    --icon assets/icon.ico \
    --add-data "assets/icon.ico;assets" \
    --version-file version.txt \
    --clean --noconfirm main.py
```

---

## 👨‍💻 Autor

**MAZNET (Mateusz Mazur)**
© 2026