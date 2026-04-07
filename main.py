###############################################
#     _____ _____ _____ _____ _____ _____     #
#    |     |  _  |__   |   | |   __|_   _|    #
#    | | | |     |   __| | | |   __| | |      #
#    |_|_|_|__|__|_____|_|___|_____| |_|      #
#                                             #
#          Copyright (c) 2026 MAZNET          #
#       Author: MAZNET (Mateusz Mazur)        #
#                                             #
###############################################

# ============================================================
# IMPORTY
# ============================================================
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from theme.global_qss import get_stylesheet

# ============================================================
# POMOCNICZA FUNKCJA DO ZASOBÓW (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ============================================================
# GŁÓWNY RDZEŃ PROGRAMU
# ============================================================
def main():
    app = QApplication(sys.argv)

    # === IKONA APLIKACJI ===
    app.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

    # === Ładowanie stylów ===
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
