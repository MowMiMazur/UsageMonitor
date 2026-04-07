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
# STAŁE APLIKACJI
# ============================================================
APP_NAME = "UsageMonitor"
VERSION = "1.0.1"
VERSION_TAG = ""
APP_AUTHOR_TEXT = "Stworzone z ❤️ przez MAZNET"

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 440

# ============================================================
# FUNKCJE POMOCNICZE
# ============================================================
def get_full_version():
    if VERSION_TAG:
        return f"v{VERSION} ({VERSION_TAG})"
    return f"v{VERSION}"
