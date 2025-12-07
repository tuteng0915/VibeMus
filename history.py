"""History persistence helpers for VibeMus.

Provides utilities to store each generated audio snapshot together with
lyrics/tags metadata and query existing entries.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydub import AudioSegment

HISTORY_DIR = Path('history')
HISTORY_AUDIO_DIR = HISTORY_DIR / 'audio'
HISTORY_LOG = HISTORY_DIR / 'logs.json'

__all__ = [
    'HISTORY_DIR',
    'HISTORY_AUDIO_DIR',
    'HISTORY_LOG',
    'ensure_history_storage',
    'read_history_entries',
    'write_history_entries',
    'log_audio_snapshot',
    'find_history_entry_by_display',
    'find_history_entry_by_id',
]


def ensure_history_storage():
    HISTORY_DIR.mkdir(exist_ok=True)
    HISTORY_AUDIO_DIR.mkdir(exist_ok=True)
    if not HISTORY_LOG.exists():
        HISTORY_LOG.write_text('[]', encoding='utf-8')


def read_history_entries() -> List[Dict]:
    ensure_history_storage()
    try:
        with open(HISTORY_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def write_history_entries(entries: List[Dict]):
    ensure_history_storage()
    with open(HISTORY_LOG, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def _first_lyric_line(lyrics: str) -> str:
    for line in lyrics.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ''


def _slugify_label(text: str) -> str:
    safe = re.sub(r'[^0-9A-Za-z]+', '_', text).strip('_')
    return safe[:40] or 'entry'


def _get_audio_duration_seconds(path: str):
    try:
        return AudioSegment.from_file(path).duration_seconds
    except Exception:
        return None


def log_audio_snapshot(audio_path, lyrics, tags, duration=None):
    """Persist audio, lyrics, and tags into history storage."""
    if not audio_path or not os.path.exists(audio_path):
        return None

    ensure_history_storage()
    entries = read_history_entries()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    first_line = _first_lyric_line(lyrics)
    label = first_line or timestamp
    slug = _slugify_label(first_line) if first_line else timestamp
    dest_name = f'{timestamp}_{slug}.wav'
    dest_path = HISTORY_AUDIO_DIR / dest_name
    shutil.copy(audio_path, dest_path)
    duration = duration or _get_audio_duration_seconds(str(dest_path))
    entry = {
        'id': f'{timestamp}_{slug}',
        'timestamp': timestamp,
        'label': label,
        'display': f'{timestamp} - {label[:60]}',
        'lyrics': lyrics,
        'tags': tags,
        'audio_path': str(dest_path),
        'duration': duration,
    }
    entries.append(entry)
    write_history_entries(entries)
    return entry


def find_history_entry_by_display(display_value) -> Optional[Dict]:
    for entry in read_history_entries():
        if entry['display'] == display_value:
            return entry
    return None


def find_history_entry_by_id(entry_id: str) -> Optional[Dict]:
    for entry in read_history_entries():
        if entry['id'] == entry_id:
            return entry
    return None
