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
from .theme import Theme

# ============================================================
# GENERATOR STYLÓW (QSS)
# ============================================================
def get_stylesheet():
    return f"""
    QWidget {{
        background-color: {Theme.BACKGROUND};
        color: {Theme.TEXT};
        font-family: {Theme.FONT_FAMILY};
        font-size: {Theme.font_size_base};
    }}

    QMainWindow {{
        background-color: {Theme.BACKGROUND};
    }}
    
    /* --- Labels --- */
    QLabel {{
        color: {Theme.TEXT};
        background: transparent;
    }}
    
    QLabel#secondary_text {{
        color: {Theme.TEXT_SECONDARY};
        font-size: {Theme.font_size_small};
        background: transparent;
    }}

    QLabel#h1 {{
        font-size: 24px;
        font-weight: bold;
        color: {Theme.TEXT};
        margin-bottom: 10px;
    }}

    QLabel#version_label {{
        color: {Theme.TEXT_SECONDARY};
        font-size: {Theme.font_size_tiny};
        margin-top: 5px;
    }}

    QLabel#timer_label {{
        color: {Theme.PRIMARY};
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
    }}

    /* --- Containers/Cards --- */
    QFrame#card {{
        background-color: {Theme.SURFACE};
        border: 1px solid {Theme.INPUT_BORDER};
        border-radius: {Theme.BORDER_RADIUS};
    }}

    /* --- Inputs --- */
    QLineEdit {{
        border: 1px solid {Theme.INPUT_BORDER};
        border-radius: {Theme.BORDER_RADIUS};
        padding: 10px 12px;
        background-color: {Theme.INPUT_BG};
        color: {Theme.TEXT};
        selection-background-color: {Theme.PRIMARY};
        selection-color: {Theme.TEXT_INVERSE};
    }}
    
    QLineEdit:hover {{
        border: 1px solid #6c757d;
    }}

    QLineEdit:focus {{
        border: 1px solid {Theme.INPUT_FOCUS_BORDER};
        background-color: {Theme.INPUT_BG};
    }}

    QLineEdit:disabled {{
        background-color: {Theme.SURFACE};
        color: {Theme.TEXT_SECONDARY};
        border: 1px solid {Theme.SURFACE};
    }}

    /* --- Buttons --- */
    QPushButton {{
        background-color: {Theme.PRIMARY};
        color: {Theme.TEXT_INVERSE};
        border: 1px solid transparent;
        border-radius: {Theme.BORDER_RADIUS};
        padding: 10px 20px;
        min-height: 20px;
        font-weight: 500;
        font-family: {Theme.FONT_FAMILY};
    }}

    QPushButton:hover {{
        background-color: {Theme.PRIMARY_HOVER};
    }}

    QPushButton:pressed {{
        background-color: {Theme.PRIMARY_PRESSED};
    }}

    QPushButton:disabled {{
        background-color: {Theme.PRIMARY_DISABLED};
        color: rgba(255,255,255, 0.6);
        border: 1px solid transparent;
    }}

    /* Specific Button: Browse/Secondary */
    QPushButton#browse_btn {{
        background-color: {Theme.SURFACE};
        color: {Theme.TEXT};
        border: 1px solid {Theme.INPUT_BORDER};
        font-weight: normal; 
    }}
    
    QPushButton#browse_btn:hover {{
        background-color: {Theme.SURFACE_HOVER};
        border: 1px solid {Theme.TEXT_SECONDARY};
    
    QPushButton#browse_btn:disabled {{
        background-color: {Theme.SURFACE};
        color: {Theme.PRIMARY_DISABLED};
        border: 1px solid {Theme.SURFACE};
    }}
        color: {Theme.TEXT_INVERSE};
    }}
    
    QPushButton#browse_btn:pressed {{
        background-color: {Theme.BACKGROUND};
    }}

    /* Specific Button: Action (Stop Monitoring) */
    QPushButton#action_btn {{
        font-size: {Theme.font_size_large};
        padding: 12px;
        font-weight: bold;
    }}
    
    QPushButton#action_btn[monitoring="true"] {{
        background-color: {Theme.ERROR};
    }}
    
    QPushButton#action_btn[monitoring="true"]:hover {{
        background-color: {Theme.ERROR_HOVER};
    }}

    /* --- ListWidget --- */
    QListWidget {{
        border: 1px solid {Theme.INPUT_BORDER};
        background-color: {Theme.INPUT_BG};
        border-radius: {Theme.BORDER_RADIUS};
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 10px;
        color: {Theme.TEXT};
        border-bottom: 1px solid {Theme.SURFACE};
    }}
    
    QListWidget::item:selected {{
        background-color: {Theme.PRIMARY};
        color: {Theme.TEXT_INVERSE};
        border-bottom: 1px solid {Theme.PRIMARY};
        border-radius: 4px;
    }}
    
    QListWidget::item:hover:!selected {{
        background-color: {Theme.SURFACE};
    }}

    /* --- Scrollbars --- */
    QScrollBar:vertical {{
        border: none;
        background: {Theme.BACKGROUND};
        width: 12px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {Theme.INPUT_BORDER};
        min-height: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Theme.TEXT_SECONDARY};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: {Theme.BACKGROUND};
        height: 12px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Theme.INPUT_BORDER};
        min-width: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {Theme.TEXT_SECONDARY};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        background: none;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* --- Summary Dialog Sections --- */
    QFrame#summary_section {{
        background-color: transparent;
        border: none;
        border-bottom: 1px solid {Theme.INPUT_BORDER};
        border-radius: 0px;
    }}
    
    QLabel#section_title {{
        font-weight: bold;
        color: {Theme.TEXT};
        font-size: {Theme.font_size_base};
        background: transparent;
    }}
    
    /* Stat Box (Min/Max/Avg) */
    QFrame#stat_box, QFrame#stat_box_avg {{
        background-color: {Theme.INPUT_BG};
        border-radius: 6px;
        border: 1px solid transparent; 
    }}
    
    QFrame#stat_box_avg {{
        background-color: {Theme.SURFACE};
        border: 1px solid {Theme.PRIMARY_DISABLED};
    }}
    
    QLabel#stat_label {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        background: transparent;
        margin-top: 2px;
    }}
    
    QLabel#stat_value {{
        color: {Theme.TEXT};
        font-size: 18px;
        font-weight: bold;
        background: transparent;
    }}

    /* File Path Card */
    QFrame#path_card {{
        background-color: {Theme.SURFACE};
        border: 1px solid {Theme.INPUT_BORDER};
        border-radius: {Theme.BORDER_RADIUS};
    }}

    QLabel#path_icon {{
        font-size: 24px;
        background: transparent;
        color: {Theme.TEXT_SECONDARY};
    }}
    
    QLabel#path_title {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        background: transparent;
    }}

    QLabel#path_value {{
        color: {Theme.PRIMARY};
        font-family: "Consolas", monospace;
        font-size: 13px;
        background: transparent;
        margin-top: 2px;
    }}
    """
