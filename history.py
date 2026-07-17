"""Translation history — persisted as a local JSON file."""

import json
import os
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "translation_history.json"
MAX_ENTRIES = 50


def _load() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            pass
    return []


def _save(entries: list[dict]) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
    except Exception:
        pass


def add_entry(original: str, translated: str, src: str, tgt: str) -> None:
    entries = _load()
    entry = {
        "original":   original[:300],
        "translated": translated[:300],
        "src":        src,
        "tgt":        tgt,
        "time":       datetime.now().strftime("%d %b %Y  %H:%M"),
    }
    entries.insert(0, entry)
    _save(entries[:MAX_ENTRIES])


def get_history() -> list[dict]:
    return _load()


def clear_history() -> None:
    _save([])
