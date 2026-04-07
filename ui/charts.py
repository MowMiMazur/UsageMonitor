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
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QTabWidget, 
                               QLabel, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QPainterPath, QFont

class SimpleChartWidget(QWidget):
    def __init__(self, data, title="", unit="", color="#3498db", parent=None):
        super().__init__(parent)
        self.data = data
        self.chart_title = title
        self.unit = unit
        self.line_color = QColor(color)
        self.setMinimumHeight(250)
        # self.setBackgroundRole(QWidget.NoRole) # Removed causing AttributeError

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Wymiary
        w = self.width()
        h = self.height()
        
        # Marginesy
        margin_left = 50
        margin_right = 20
        margin_top = 40
        margin_bottom = 30
        
        graph_w = w - margin_left - margin_right
        graph_h = h - margin_top - margin_bottom
        
        # Tło
        painter.fillRect(self.rect(), QColor("#ffffff")) # Białe tło dla wykresu
        
        if not self.data:
            painter.drawText(self.rect(), Qt.AlignCenter, "Brak danych")
            return

        # Skalowanie

        # Skalowanie
        min_val = min(self.data)
        max_val = max(self.data)
        
        # Dodaj lekki margines do min/max żeby wykres nie dotykał krawędzi
        val_range = max_val - min_val
        if val_range == 0:
            val_range = 1 if max_val == 0 else max_val * 0.1
            
        y_min = min_val - (val_range * 0.1)
        y_max = max_val + (val_range * 0.1)
        if y_min < 0: y_min = 0 # Nie schodź poniżej 0 dla CPU/RAM
        
        adjusted_range = y_max - y_min
        
        # Osie
        painter.setPen(QPen(QColor("#cccccc"), 1))
        # Oś Y (linia pionowa)
        painter.drawLine(margin_left, margin_top, margin_left, h - margin_bottom)
        # Oś X (linia pozioma)
        painter.drawLine(margin_left, h - margin_bottom, w - margin_right, h - margin_bottom)
        
        # Linie siatki poziomej i etykiety Y
        axis_font = painter.font()
        axis_font.setBold(False)
        axis_font.setPointSize(8)
        painter.setFont(axis_font)
        
        steps = 5
        for i in range(steps + 1):
            y_ratio = i / steps
            y_pos = h - margin_bottom - (y_ratio * graph_h)
            val = y_min + (y_ratio * adjusted_range)
            
            # Linia siatki
            painter.setPen(QPen(QColor("#eeeeee"), 1, Qt.DashLine))
            painter.drawLine(margin_left, int(y_pos), w - margin_right, int(y_pos))
            
            # Etykieta
            painter.setPen(Qt.black)
            label_text = f"{val:.1f}{self.unit}"
            painter.drawText(0, int(y_pos) - 10, margin_left - 5, 20, Qt.AlignRight | Qt.AlignVCenter, label_text)

        # Rysowanie wykresu
        if len(self.data) > 1:
            path = QPainterPath()
            
            x_step = graph_w / (len(self.data) - 1)
            
            points = []
            for i, val in enumerate(self.data):
                x = margin_left + (i * x_step)
                # Normalizacja Y: (val - y_min) / adjusted_range -> 0..1
                # Ale współrzędne ekranowe Y rosną w dół, więc:
                # y_screen = (h - margin_bottom) - (normalized * graph_h)
                normalized_val = (val - y_min) / adjusted_range
                y = (h - margin_bottom) - (normalized_val * graph_h)
                points.append(QPointF(x, y))
            
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            
            # Wypełnienie pod wykresem (gradient)
            fill_path = QPainterPath(path)
            fill_path.lineTo(points[-1].x(), h - margin_bottom)
            fill_path.lineTo(points[0].x(), h - margin_bottom)
            fill_path.closeSubpath()
            
            grad = QLinearGradient(0, margin_top, 0, h - margin_bottom)
            c1 = QColor(self.line_color)
            c1.setAlpha(100)
            c2 = QColor(self.line_color)
            c2.setAlpha(10)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawPath(fill_path)
            
            # Linia wykresu
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(self.line_color, 2))
            painter.drawPath(path)


class ChartsWindow(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wykresy wydajności")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        samples = stats.get('samples', {})
        
        # === Tab: CPU ===
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout(cpu_tab)
        
        if 'cpu_raw' in samples:
            cpu_raw_chart = SimpleChartWidget(samples['cpu_raw'], "Użycie CPU (Raw)", "%", "#e74c3c")
            cpu_layout.addWidget(cpu_raw_chart)
            
        if 'cpu_norm' in samples:
            cpu_norm_chart = SimpleChartWidget(samples['cpu_norm'], "Użycie CPU (Znormalizowane - podzielone przez liczbę rdzeni)", "%", "#e67e22")
            cpu_layout.addWidget(cpu_norm_chart)
            
        self.tabs.addTab(cpu_tab, "CPU")
        
        # === Tab: RAM ===
        ram_tab = QWidget()
        ram_layout = QVBoxLayout(ram_tab)
        
        if 'ram' in samples:
            ram_chart = SimpleChartWidget(samples['ram'], "Zużycie pamięci RAM", " MB", "#3498db")
            ram_layout.addWidget(ram_chart)
            
        self.tabs.addTab(ram_tab, "RAM")
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QFrame() # Placeholder for button if I wanted one, but QDialog has X.
        # Let's add explicit Close button
        from PySide6.QtWidgets import QPushButton
        close_btn = QPushButton("Zamknij")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
