APP_NAME = "UsageMonitor"
VERSION = "2.0.2"
VERSION_TAG = ""

AUTHOR_NAME = "MAZNET"
AUTHOR_URL = "https://maznet.pl"

WINDOW_WIDTH = 760
WINDOW_HEIGHT = 800

# --- Update check (maznet.pl public API) ---
UPDATE_SLUG = "usagemonitor"
UPDATE_API_URL = "https://maznet.pl/api/v1/updates"
UPDATE_FALLBACK_PAGE = f"{AUTHOR_URL}/aplikacje/{UPDATE_SLUG}"
UPDATE_TIMEOUT = 8          # seconds for a single HTTP request
UPDATE_MIN_INTERVAL = 3600       # don't hit the network more often than this


def get_full_version():
    if VERSION_TAG:
        return f"v{VERSION} ({VERSION_TAG})"
    return f"v{VERSION}"
