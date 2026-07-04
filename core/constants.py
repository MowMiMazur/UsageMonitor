APP_NAME = "UsageMonitor"
VERSION = "2.0.0"
VERSION_TAG = ""

AUTHOR_NAME = "MAZNET"
AUTHOR_URL = "https://maznet.pl"

WINDOW_WIDTH = 760
WINDOW_HEIGHT = 800


def get_full_version():
    if VERSION_TAG:
        return f"v{VERSION} ({VERSION_TAG})"
    return f"v{VERSION}"
