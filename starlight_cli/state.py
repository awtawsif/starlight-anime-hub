import json
from pathlib import Path
from typing import Optional

STATE_DIR = Path.home() / ".starlight"
STATE_FILE = STATE_DIR / "state.json"


def _ensure():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"bookmarks": {}, "watched": {}, "codes": {}, "sessions_to_codes": {}}))


def _read():
    _ensure()
    return json.loads(STATE_FILE.read_text())


def _write(data):
    _ensure()
    STATE_FILE.write_text(json.dumps(data, indent=2))


def get_bookmarks():
    return _read().get("bookmarks", {})


def add_bookmark(anime_id, title):
    data = _read()
    data.setdefault("bookmarks", {})[anime_id] = title
    _write(data)


def remove_bookmark(anime_id):
    data = _read()
    data.get("bookmarks", {}).pop(anime_id, None)
    _write(data)


def get_watched():
    return _read().get("watched", {})


def mark_watched(anime_id, episode_id):
    data = _read()
    data.setdefault("watched", {}).setdefault(anime_id, []).append(episode_id)
    _write(data)


def is_watched(anime_id, episode_id):
    return episode_id in get_watched().get(anime_id, [])


def save_code(code: str, session_id: str, title: str):
    data = _read()
    data.setdefault("codes", {})[code] = {"session_id": session_id, "title": title}
    data.setdefault("sessions_to_codes", {})[session_id] = code
    _write(data)


def get_code_info(code: str) -> Optional[dict]:
    return _read().get("codes", {}).get(code)


def get_all_codes() -> dict:
    return _read().get("codes", {})


def get_session_code(session_id: str) -> Optional[str]:
    return _read().get("sessions_to_codes", {}).get(session_id)
