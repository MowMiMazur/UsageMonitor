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
import os
import sys
import psutil
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal, QEvent, QTimer, QTime, QElapsedTimer
from PySide6.QtGui import QIcon, QIntValidator

from ui.dialogs import ProcessSelectionDialog, SummaryDialog, CustomMessageBox
from core.monitor import MonitorThread
from core.constants import APP_NAME, get_full_version, WINDOW_WIDTH, WINDOW_HEIGHT, APP_AUTHOR_TEXT

from theme.theme import Theme

# ============================================================
# KLASA OVERLAY
# ============================================================
class Overlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {Theme.OVERLAY_BG};")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.hide()

    def set_target(self, widget):
        self.setParent(widget)
        self.resize(widget.size())
        self.show()

# ============================================================
# GŁÓWNE OKNO APLIKACJI
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {get_full_version()}")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # === Widget centralny ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # === Główny układ ===
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        
        # === Nagłówek ===
        header_lbl = QLabel(APP_NAME)
        header_lbl.setObjectName("h1")
        header_lbl.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header_lbl)
        
        # === Karta wejściowa ===
        self.card_frame = QFrame()
        self.card_frame.setObjectName("card")
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # === Wiersz wyboru PID ===
        pid_row = QHBoxLayout()
        
        pid_lbl = QLabel("PID:")
        pid_lbl.setObjectName("secondary_text")
        pid_row.addWidget(pid_lbl)
        
        self.pid_input = QLineEdit()
        self.pid_input.setValidator(QIntValidator(0, 999999))
        self.pid_input.setPlaceholderText("np. 1234")
        self.pid_input.setAlignment(Qt.AlignCenter)
        
        self.browse_btn = QPushButton("Wybierz program")
        self.browse_btn.setObjectName("browse_btn")
        self.browse_btn.clicked.connect(self.browse_process)
        
        pid_row.addWidget(self.pid_input)
        pid_row.addWidget(self.browse_btn)
        
        card_layout.addLayout(pid_row)
        
        # === Przycisk akcji ===
        self.action_btn = QPushButton("Rozpocznij monitoring")
        self.action_btn.setObjectName("action_btn")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.toggle_monitoring)
        card_layout.addWidget(self.action_btn)
        
        # === Licznik czasu ===
        self.timer_lbl = QLabel("00:00:00")
        self.timer_lbl.setObjectName("timer_label")
        self.timer_lbl.setAlignment(Qt.AlignCenter)
        self.timer_lbl.hide()
        card_layout.addWidget(self.timer_lbl)
        
        self.main_layout.addWidget(self.card_frame)
        
        # === Spacer ===
        self.main_layout.addStretch()
        
        # === Stopka ===
        footer_container = QWidget()
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(2) # Minimal spacing
        
        # === Stopka (Wersja) ===
        self.version_lbl = QLabel(get_full_version())
        self.version_lbl.setObjectName("version_label")
        self.version_lbl.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.version_lbl)
        
        # === Stopka (Autor) ===
        self.author_lbl = QLabel(APP_AUTHOR_TEXT)
        self.author_lbl.setObjectName("version_label")
        self.author_lbl.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.author_lbl)
        
        self.main_layout.addWidget(footer_container)

        # === Wątek monitorowania ===
        self.monitor_thread = None
        
        # === Timer do odświeżania czasu trwania ===
        self.display_timer = QTimer()
        self.display_timer.setInterval(1000)
        self.display_timer.timeout.connect(self.update_timer_label)
        self.elapsed_timer = QElapsedTimer()
        
    # === Metoda do obsługi przycisku wyboru procesu ===
    def browse_process(self):
        dialog = ProcessSelectionDialog(self)
        if dialog.exec():
            pid = dialog.get_selected_pid()
            if pid:
                self.pid_input.setText(str(pid))

    # === Metoda do obsługi przycisku start/stop monitorowania ===
    def toggle_monitoring(self):
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.stop_monitoring()
        else:
            self.start_monitoring()

    # === Metoda do rozpoczęcia monitorowania ===
    def start_monitoring(self):
        pid_text = self.pid_input.text().strip()
        if not pid_text.isdigit():
            CustomMessageBox("Błąd", "Proszę podać poprawny numer PID (liczba).", "warning", self).exec()
            return
            
        pid = int(pid_text)
        
        try:
            process = psutil.Process(pid)
            proc_name = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = "unknown"

        safe_name = "".join(c for c in proc_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_name:
            safe_name = "process"
            
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        logs_dir = os.path.join(base_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        filename = f"{pid}-{safe_name}-usagemonitor.log"
        output_path = os.path.join(logs_dir, filename)

        self.monitor_thread = MonitorThread(pid, output_path)
        self.monitor_thread.finished.connect(self.on_monitoring_finished)
        self.monitor_thread.error.connect(self.on_monitoring_error)
        
        self.monitor_thread.start()
        self.set_monitoring_state(True)
        
        # === Start Timera ===
        self.elapsed_timer.start()
        self.update_timer_label()
        self.display_timer.start()
        self.timer_lbl.show()

    # === Metoda do zatrzymania monitorowania ===
    def stop_monitoring(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.action_btn.setText("Zatrzymywanie...")
            self.action_btn.setEnabled(False)

    # === Metoda do aktualizacji stanu interfejsu podczas monitorowania ===
    def set_monitoring_state(self, is_monitoring):
        if is_monitoring:
            # === Zablokuj tylko pola wejściowe ===
            self.pid_input.setEnabled(False)
            self.browse_btn.setEnabled(False)
            
            # === Zmień stan przycisku ===
            self.action_btn.setText("Zatrzymaj monitoring")
            self.action_btn.setProperty("monitoring", True)
            self.action_btn.style().unpolish(self.action_btn)
            self.action_btn.style().polish(self.action_btn)
        else:
            # === Stop Timer ===
            self.display_timer.stop()
            self.timer_lbl.hide()
            
            # === Odblokuj pola wejściowe ===
            self.pid_input.setEnabled(True)
            self.browse_btn.setEnabled(True)
            
            # === Zresetuj stan przycisku ===
            self.action_btn.setText("Rozpocznij monitoring")
            self.action_btn.setProperty("monitoring", False)
            self.action_btn.setEnabled(True)
            self.action_btn.style().unpolish(self.action_btn)
            self.action_btn.style().polish(self.action_btn)

    # === Slot do aktualizacji licznika czasu ===
    def update_timer_label(self):
        elapsed = self.elapsed_timer.elapsed() # ms
        s = elapsed // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        self.timer_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")

    # === Sloty do obsługi zakończenia monitorowania i błędów ===
    def on_monitoring_finished(self, stats):
        self.set_monitoring_state(False)
        self.monitor_thread = None
        
        SummaryDialog(stats, self).exec()

    # === Slot do obsługi błędów monitorowania ===
    def on_monitoring_error(self, error_msg):
        self.set_monitoring_state(False)
        self.monitor_thread = None
        CustomMessageBox("Błąd monitorowania", error_msg, "error", self).exec()

    # === Metoda do obsługi zamykania okna (zatrzymanie wątku) ===
    def closeEvent(self, event):
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        super().closeEvent(event)
