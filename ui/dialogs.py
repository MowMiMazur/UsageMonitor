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

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QListWidget, QLabel, 
                               QListWidgetItem, QLineEdit, QWidget, QFrame)
from PySide6.QtCore import Qt
from core.utils import get_process_list
from ui.charts import ChartsWindow

# ============================================================
# NIESTANDARDOWY KOMUNIKAT
# ============================================================
class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon_type="error", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        
        icon_map = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon_char = icon_map.get(icon_type, "ℹ️")
        
        icon_lbl = QLabel(icon_char)
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignTop)
        content_row.addWidget(icon_lbl)
        
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        msg_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        content_row.addWidget(msg_lbl, 1)
        
        layout.addLayout(content_row)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)

# ============================================================
# WYBÓR PROCESU
# ============================================================
class ProcessSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz program")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # === Wyszukiwarka ===
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Szukaj procesu...")
        self.search_input.textChanged.connect(self.filter_processes)
        layout.addWidget(self.search_input)

        # === Lista procesów ===
        self.process_list_widget = QListWidget()
        layout.addWidget(self.process_list_widget)
        
        # ===  Przyciski akcji ===
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Anuluj")
        self.select_btn = QPushButton("Wybierz")
        self.select_btn.setEnabled(False)  # Disabled until selection
        
        self.cancel_btn.clicked.connect(self.reject)
        self.select_btn.clicked.connect(self.accept_selection)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.select_btn)
        layout.addLayout(button_layout)
        
        self.process_list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.process_list_widget.itemDoubleClicked.connect(self.accept_selection)
        
        self.all_processes = []
        self.load_processes()
        
    # === Wczytywanie ===
    def load_processes(self):
        self.process_list_widget.clear()
        self.all_processes = get_process_list()
        self.filter_processes("")
    
    # === Filtrowanie ===
    def filter_processes(self, text):
        self.process_list_widget.clear()
        search_text = text.lower()
        for pid, name in self.all_processes:
            if search_text in name.lower() or str(pid) in search_text:
                item = QListWidgetItem(f"{name} (PID: {pid})")
                item.setData(Qt.UserRole, pid)
                self.process_list_widget.addItem(item)

    # === Obsługa wyboru ===            
    def on_selection_changed(self):
        self.select_btn.setEnabled(len(self.process_list_widget.selectedItems()) > 0)

    # === Akceptacja wyboru === 
    def accept_selection(self):
        if self.process_list_widget.selectedItems():
            self.accept()

    # === Pobranie wybranego PID ===     
    def get_selected_pid(self):
        if self.process_list_widget.selectedItems():
            return self.process_list_widget.selectedItems()[0].data(Qt.UserRole)
        return None

# ============================================================
# PODSUMOWANIE (RAPORT)
# ============================================================
class SummaryDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Raport moniotorowania")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        if not stats.get('has_data'):
            layout.addWidget(QLabel("Brak danych pomiarowych."))
        else:
            # === Czas ===
            if 'start_str' in stats:
                self.add_time_section(layout, stats['start_str'], stats['end_str'], stats['duration_str'])

            # === CPU (Na rdzeń) ===
            raw = stats['cpu_raw'] # min, max, avg
            self.add_section(layout, "⚡ CPU (Na rdzeń)", raw, "%")

            # === CPU (Całkowite) ===
            norm = stats['cpu_norm']
            self.add_section(layout, "📊 CPU (Całkowite)", norm, "%")

            # === RAM ===
            ram = stats['ram']
            self.add_section(layout, "💾 Pamięć RAM", ram, " MB")

            # === Ścieżka do pliku ===
            path_card = QFrame()
            path_card.setObjectName("path_card")
            card_layout = QHBoxLayout(path_card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            card_layout.setSpacing(16)

            # === Icon ===
            icon_lbl = QLabel("📂")
            icon_lbl.setObjectName("path_icon")
            icon_lbl.setAlignment(Qt.AlignTop | Qt.AlignCenter)
            card_layout.addWidget(icon_lbl)
            
            # === Kontener tekstu ===
            text_container = QWidget()
            text_container.setStyleSheet("background-color: transparent;")
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(0,0,0,0)
            text_layout.setSpacing(4)
            
            lbl_info = QLabel("Logi zostały zapisane w:")
            lbl_info.setObjectName("path_title")
            text_layout.addWidget(lbl_info)
            
            lbl_path = QLabel(stats.get('output_file', ''))
            lbl_path.setObjectName("path_value")
            lbl_path.setWordWrap(True)
            lbl_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
            text_layout.addWidget(lbl_path)
            
            card_layout.addWidget(text_container, 1) # 1 stretch factor
            
            layout.addWidget(path_card)

        # === Przyciski zamykania ===
        btn_layout = QHBoxLayout()
        
        if stats.get('has_data') and 'samples' in stats:
            charts_btn = QPushButton("Pokaż wykresy")
            charts_btn.setMinimumWidth(120)
            charts_btn.setCursor(Qt.PointingHandCursor)
            # Stylowanie przycisku (opcjonalne, ale pasujące do reszty)
            charts_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            charts_btn.clicked.connect(lambda: self.show_charts(stats))
            btn_layout.addWidget(charts_btn)
            
        btn_layout.addStretch()
        close_btn = QPushButton("Zamknij")
        close_btn.setMinimumWidth(120)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)

    def show_charts(self, stats):
        win = ChartsWindow(stats, self)
        win.exec()

    # === Metoda pomocnicza do dodawania sekcji czasu ===
    def add_time_section(self, layout, start, end, duration):
        container = QFrame()
        container.setObjectName("summary_section")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(16)
        
        title_lbl = QLabel("⏱️ Czas monitorowania")
        title_lbl.setObjectName("section_title")
        vbox.addWidget(title_lbl)
        
        stats_container = QWidget()
        hbox = QHBoxLayout(stats_container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(12)
        
        def create_box(label, value, is_highlighted=False):
            box = QFrame()
            box.setObjectName("stat_box_avg" if is_highlighted else "stat_box")
            
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 12, 0, 12)
            box_layout.setSpacing(4)
            
            lbl = QLabel(label)
            lbl.setObjectName("stat_label")
            lbl.setAlignment(Qt.AlignCenter)
            
            val = QLabel(value)
            val.setObjectName("stat_value")
            val.setAlignment(Qt.AlignCenter)
            
            box_layout.addWidget(val)
            box_layout.addWidget(lbl)
            return box
            
        hbox.addWidget(create_box("START", start))
        hbox.addWidget(create_box("STOP", end))
        hbox.addWidget(create_box("ŁĄCZNIE", duration, is_highlighted=True))
        
        vbox.addWidget(stats_container)
        layout.addWidget(container)

    # === Metoda pomocnicza do dodawania sekcji z min/avg/max ===
    def add_section(self, layout, title, data, unit=""):
        min_val, max_val, avg_val = data
        
        container = QFrame()
        container.setObjectName("summary_section")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(16)
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("section_title")
        vbox.addWidget(title_lbl)
        
        stats_container = QWidget()
        hbox = QHBoxLayout(stats_container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(12)
        
        # === Funkcja pomocnicza do tworzenia boxów statystyk ===
        def create_stat_box(label, value, is_avg=False):
            box = QFrame()
            if is_avg:
                 box.setObjectName("stat_box_avg")
            else:
                 box.setObjectName("stat_box")
                 
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 12, 0, 12)
            box_layout.setSpacing(4)
            
            lbl = QLabel(label)
            lbl.setObjectName("stat_label")
            lbl.setAlignment(Qt.AlignCenter)
            
            val = QLabel(f"{value:.2f}{unit}")
            val.setObjectName("stat_value")
            val.setAlignment(Qt.AlignCenter)
            
            box_layout.addWidget(val)
            box_layout.addWidget(lbl)
            return box
            
        hbox.addWidget(create_stat_box("MIN.", min_val))
        hbox.addWidget(create_stat_box("ŚREDNIA", avg_val, is_avg=True))
        hbox.addWidget(create_stat_box("MAKS.", max_val))
        
        vbox.addWidget(stats_container)
        
        layout.addWidget(container)
