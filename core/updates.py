"""Update check against the public maznet.pl API.

    GET https://maznet.pl/api/v1/updates/{slug}?version={installed}

Read-only, no auth. The endpoint is rate limited (30 requests / 300 s per IP) and
sends an ETag, so this module keeps a small on-disk cache: the ETag is replayed as
`If-None-Match` and the previous payload is reused on 304 or on any network failure.
Nothing here raises — the caller always gets a plain dict.
"""

import os
import re
import ssl
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from core.utils import app_data_dir
from core.constants import (
    APP_NAME,
    VERSION,
    AUTHOR_URL,
    UPDATE_SLUG,
    UPDATE_API_URL,
    UPDATE_TIMEOUT,
    UPDATE_MIN_INTERVAL,
    UPDATE_FALLBACK_PAGE,
)

CACHE_FILE = "update-cache.json"
USER_AGENT = f"{APP_NAME}/{VERSION} (+{AUTHOR_URL})"

_VERSION_RE = re.compile(r"^[0-9A-Za-z.+-]{1,32}$")


# --- version comparison -------------------------------------------------

def _version_key(version):
    """('2.10.0-rc1') -> ((2, 10, 0), 0, 'rc1'); pre-releases sort below the release."""
    text = str(version or "").strip().lstrip("vV")
    match = re.match(r"^([0-9]+(?:\.[0-9]+)*)(.*)$", text)
    head, tail = (match.group(1), match.group(2)) if match else ("", text)
    numbers = tuple(int(n) for n in head.split(".") if n.isdigit())
    numbers = (numbers + (0, 0, 0))[:4]
    suffix = tail.lstrip("-+").lower()
    return (numbers, 0 if suffix else 1, suffix)


def strip_prefix(version):
    """'v2.1.0' -> '2.1.0'; the API may or may not carry the tag prefix."""
    return str(version or "").strip().lstrip("vV") or None


def is_newer(latest, current):
    """True when `latest` is a strictly higher version than `current`."""
    if not latest or not current:
        return False
    try:
        return _version_key(latest) > _version_key(current)
    except (TypeError, ValueError):
        return False


# --- cache --------------------------------------------------------------

def _cache_path():
    return os.path.join(app_data_dir(), CACHE_FILE)


def _load_cache():
    try:
        with open(_cache_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("for_version") != VERSION:
        return {}  # a fresh install invalidates the stored verdict
    return data


def _save_cache(data):
    data["for_version"] = VERSION
    try:
        with open(_cache_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass


# --- HTTP ---------------------------------------------------------------

def _request(etag):
    """Return (status, payload_or_None, etag_or_None, retry_after_seconds)."""
    query = urllib.parse.urlencode({"version": VERSION})
    url = f"{UPDATE_API_URL}/{urllib.parse.quote(UPDATE_SLUG)}?{query}"

    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", USER_AGENT)
    if etag:
        request.add_header("If-None-Match", etag)

    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=UPDATE_TIMEOUT, context=context) as response:
            status = response.getcode()
            body = response.read(256 * 1024).decode("utf-8", "replace")
            new_etag = response.headers.get("ETag")
            return status, json.loads(body) if body.strip() else None, new_etag, 0
    except urllib.error.HTTPError as e:
        retry_after = 0
        try:
            retry_after = int(e.headers.get("Retry-After") or 0)
        except (TypeError, ValueError):
            retry_after = 0
        if e.code == 304:
            return 304, None, e.headers.get("ETag") or etag, 0
        return e.code, None, None, retry_after
    except (urllib.error.URLError, ssl.SSLError, ValueError, OSError):
        return 0, None, None, 0


_ERROR_BY_STATUS = {
    400: "bad_request",
    404: "not_found",
    405: "bad_request",
    429: "rate_limited",
    503: "unavailable",
}


# --- public API ---------------------------------------------------------

def _verdict(payload, from_cache):
    """Shape the API payload into the flat dict the UI consumes."""
    program = (payload or {}).get("program") or {}
    update = (payload or {}).get("update") or {}
    latest = strip_prefix(program.get("version") or update.get("latest"))

    available = update.get("available")
    if not isinstance(available, bool):
        available = is_newer(latest, VERSION)

    download = program.get("download")
    if isinstance(download, dict) and download.get("url"):
        download = dict(download, version=strip_prefix(download.get("version")))
    else:
        download = None

    return {
        "ok": True,
        "available": bool(available) and is_newer(latest, VERSION),
        "current": VERSION,
        "latest": latest,
        "name": program.get("name") or APP_NAME,
        "page": program.get("page") or UPDATE_FALLBACK_PAGE,
        "released_at": program.get("released_at"),
        "channel": program.get("channel"),
        "download": download,
        "from_cache": bool(from_cache),
        "checked_at": int(time.time()),
    }


def check(force=False):
    """Check for a newer release. Never raises; returns a dict with ok/available."""
    if not _VERSION_RE.match(VERSION or ""):
        return {"ok": False, "error": "bad_request", "current": VERSION,
                "page": UPDATE_FALLBACK_PAGE}

    cache = _load_cache()
    now = time.time()
    cached_payload = cache.get("payload")

    # Honour our own back-off and the server's Retry-After before touching the network.
    quiet_until = max(
        float(cache.get("retry_until") or 0),
        0 if force else float(cache.get("checked_at") or 0) + UPDATE_MIN_INTERVAL,
    )
    if now < quiet_until and cached_payload:
        return _verdict(cached_payload, from_cache=True)

    status, payload, etag, retry_after = _request(cache.get("etag"))

    if status == 200 and payload and payload.get("status") == "success":
        _save_cache({"etag": etag, "checked_at": now, "payload": payload})
        return _verdict(payload, from_cache=False)

    if status == 304 and cached_payload:
        cache.update({"checked_at": now, "etag": etag or cache.get("etag")})
        _save_cache(cache)
        return _verdict(cached_payload, from_cache=True)

    if status == 429:
        cache["retry_until"] = now + max(retry_after, 300)
        _save_cache(cache)

    if cached_payload:  # the network hiccuped — the last known answer still stands
        return _verdict(cached_payload, from_cache=True)

    return {
        "ok": False,
        "error": _ERROR_BY_STATUS.get(status, "network"),
        "status": status,
        "current": VERSION,
        "page": UPDATE_FALLBACK_PAGE,
    }
