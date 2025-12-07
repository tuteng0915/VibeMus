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
from typing import Dict, Iterable, List, Optional

from pydub import AudioSegment

REPO_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = (REPO_ROOT / 'outputs')
HISTORY_DIR = REPO_ROOT / 'history'
HISTORY_AUDIO_DIR = HISTORY_DIR / 'audio'
HISTORY_LOG = HISTORY_DIR / 'logs.json'
DEMO_AUDIO_DIR = REPO_ROOT / 'selections'
DEMO_LYRICS_DIR = REPO_ROOT / 'experiments' / 'demo' / 'test_data' / 'lyrics_and_tags'
DEMO_DIALOG_DIR = REPO_ROOT / 'experiments' / 'demo' / 'test_data' / 'dialogs'
DEFAULT_DEMO_IDS = ['bmerqe', 'pd1qwq', 'pqhby2']

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
    'seed_history_from_demo',
    'seed_default_demo_history',
    'seed_outputs_history',
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
            entries = json.load(f)
    except json.JSONDecodeError:
        entries = []
    changed = False
    for entry in entries:
        if 'display' not in entry or not entry['display']:
            entry['display'] = _build_display(entry)
            changed = True
        if _ensure_audio_local(entry):
            changed = True
        if _ensure_demo_chat(entry):
            changed = True
    if changed:
        write_history_entries(entries)
    return entries


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


def _build_display(entry: Dict) -> str:
    timestamp = entry.get('timestamp') or datetime.now().strftime('%Y%m%d_%H%M%S')
    nickname = entry.get('nickname')
    label = nickname or entry.get('label') or entry.get('id') or 'entry'
    label = label[:60]
    return f'{timestamp} - {label}'


def _repo_relative(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _get_audio_duration_seconds(path: str):
    try:
        return AudioSegment.from_file(path).duration_seconds
    except Exception:
        return None


def log_audio_snapshot(
    audio_path,
    lyrics,
    tags,
    duration=None,
    nickname: Optional[str] = None,
    entry_id: Optional[str] = None,
    copy_audio: Optional[bool] = None,
    metadata: Optional[Dict] = None,
    input_params_path: Optional[str] = None,
    chat_history: Optional[List[Dict]] = None,
):
    """Persist audio, lyrics, and tags into history storage."""
    if not audio_path or not os.path.exists(audio_path):
        return None

    ensure_history_storage()
    entries = read_history_entries()
    existing_entry = None
    if entry_id:
        for entry in entries:
            if entry.get('id') == entry_id:
                existing_entry = entry
                break
    src_path = Path(audio_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    first_line = _first_lyric_line(lyrics)
    label = first_line or timestamp
    slug = _slugify_label(first_line) if first_line else timestamp
    if copy_audio is None:
        copy_audio = True

    if existing_entry:
        updated = False

        def _update_field(key, value):
            nonlocal updated
            if value is not None and (existing_entry.get(key) != value):
                existing_entry[key] = value
                updated = True

        if lyrics:
            _update_field('lyrics', lyrics)
        if tags:
            _update_field('tags', tags)
        if nickname and not existing_entry.get('nickname'):
            _update_field('nickname', nickname)
        if metadata or input_params_path:
            merged = existing_entry.get('metadata', {}).copy()
            before = dict(merged)
            if metadata:
                merged.update(metadata)
            if input_params_path:
                merged['input_params_path'] = input_params_path
            if merged != before:
                existing_entry['metadata'] = merged
                updated = True
        if chat_history:
            _update_field('chat_history', chat_history)
        if copy_audio and src_path.exists():
            new_path = _copy_audio_to_history(src_path, existing_entry.get('id'), existing_entry.get('timestamp'))
            if new_path:
                _update_field('audio_path', _repo_relative(new_path))
        if _ensure_audio_local(existing_entry):
            updated = True
        if updated:
            existing_entry['display'] = _build_display(existing_entry)
            write_history_entries(entries)
        return existing_entry

    if copy_audio and src_path.exists():
        dest_path = _copy_audio_to_history(src_path, entry_id or f'{timestamp}_{slug}', timestamp)
    else:
        dest_path = src_path
    duration = duration or _get_audio_duration_seconds(str(dest_path))
    if not input_params_path:
        guess = dest_path.with_name(dest_path.stem + '_input_params.json')
        if not guess.exists():
            guess = src_path.with_name(src_path.stem + '_input_params.json')
        if guess.exists():
            input_params_path = _repo_relative(guess)
    entry_metadata = metadata.copy() if metadata else {}
    if input_params_path:
        entry_metadata['input_params_path'] = input_params_path
    entry = {
        'id': entry_id or f'{timestamp}_{slug}',
        'timestamp': timestamp,
        'label': label,
        'lyrics': lyrics,
        'tags': tags,
        'audio_path': _repo_relative(dest_path),
        'duration': duration,
    }
    if nickname:
        entry['nickname'] = nickname
    if entry_metadata:
        entry['metadata'] = entry_metadata
    if chat_history:
        entry['chat_history'] = chat_history
    entry['display'] = _build_display(entry)
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


def _parse_lyrics_tags_file(path: Path):
    tags_lines = []
    lyrics_lines = []
    section = None
    with open(path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            stripped = line.strip().lower()
            if stripped.startswith('tags'):
                section = 'tags'
                continue
            if stripped.startswith('lyrics'):
                section = 'lyrics'
                continue
            if section == 'tags':
                tags_lines.append(line.strip())
            elif section == 'lyrics':
                lyrics_lines.append(line)
    tags = '\n'.join(l for l in tags_lines if l)
    lyrics = '\n'.join(lyrics_lines).strip()
    return tags, lyrics


def _parse_demo_dialog(path: Path):
    if not path.exists():
        return []
    messages = []
    current_role = None
    current_lines = []

    def _flush():
        if current_role and current_lines:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_lines).strip()
            })

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if stripped.endswith(':'):
                role_token = stripped[:-1].strip().lower()
                if role_token in ('user', 'agent'):
                    _flush()
                    current_role = 'user' if role_token == 'user' else 'assistant'
                    current_lines = []
                    continue
            current_lines.append(line)
    _flush()
    return [m for m in messages if m['content']]


def _parse_demo_dialog(path: Path):
    if not path.exists():
        return []
    messages = []
    current_role = None
    current_lines = []
    def _flush():
        if current_role and current_lines:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_lines).strip()
            })
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            stripped = line.strip()
            if stripped.endswith(':') and stripped[:-1].lower() in ('user', 'agent'):
                _flush()
                role_key = stripped[:-1].lower()
                current_role = 'user' if role_key == 'user' else 'assistant'
                current_lines = []
                continue
            current_lines.append(line)
    _flush()
    return [m for m in messages if m['content']]


def seed_history_from_demo(demo_ids: Iterable[str], audio_dir=DEMO_AUDIO_DIR, lyrics_dir=DEMO_LYRICS_DIR):
    ensure_history_storage()
    entries = read_history_entries()
    existing_ids = {entry.get('id') for entry in entries}
    created = []
    for demo_id in demo_ids:
        entry_id = f'demo_{demo_id}'
        if entry_id in existing_ids:
            continue
        audio_path = Path(audio_dir) / f'{demo_id}.wav'
        lyrics_path = Path(lyrics_dir) / f'{demo_id}.txt'
        dialog_path = Path(DEMO_DIALOG_DIR) / f'{demo_id}.txt'
        if not audio_path.exists() or not lyrics_path.exists():
            continue
        tags, lyrics = _parse_lyrics_tags_file(lyrics_path)
        chat_history = _parse_demo_dialog(dialog_path)
        entry = log_audio_snapshot(
            audio_path=str(audio_path),
            lyrics=lyrics,
            tags=tags,
            nickname=f'Demo {demo_id}',
            entry_id=entry_id,
            metadata={'source': 'demo', 'demo_id': demo_id},
            copy_audio=True,
            chat_history=chat_history,
        )
        if entry:
            existing_ids.add(entry['id'])
            created.append(entry)
    return created


def seed_default_demo_history():
    return seed_history_from_demo(DEFAULT_DEMO_IDS)


def seed_outputs_history():
    ensure_history_storage()
    entries = read_history_entries()
    existing_ids = {entry.get('id') for entry in entries}
    created = []
    for wav in sorted(OUTPUTS_DIR.glob('*.wav')):
        entry_id = f'output_{wav.stem}'
        if entry_id in existing_ids:
            continue
        json_path = wav.with_name(f'{wav.stem}_input_params.json')
        if not json_path.exists():
            continue
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                params = json.load(f)
        except json.JSONDecodeError:
            continue
        lyrics = params.get('lyrics', '')
        tags = params.get('prompt', '')
        duration = params.get('audio_duration')
        entry = log_audio_snapshot(
            audio_path=str(wav),
            lyrics=lyrics,
            tags=tags,
            duration=duration,
            entry_id=entry_id,
            metadata={'source': 'output'},
            input_params_path=_repo_relative(json_path),
        )
        if entry:
            existing_ids.add(entry['id'])
            created.append(entry)
    return created


def _copy_audio_to_history(src_path: Path, entry_id: Optional[str], timestamp: Optional[str]):
    if not src_path.exists():
        return None
    suffix = src_path.suffix or '.wav'
    base = entry_id or (timestamp or datetime.now().strftime('%Y%m%d_%H%M%S'))
    safe_base = _slugify_label(base)
    dest_path = HISTORY_AUDIO_DIR / f'{safe_base}{suffix}'
    counter = 1
    while dest_path.exists():
        dest_path = HISTORY_AUDIO_DIR / f'{safe_base}_{counter}{suffix}'
        counter += 1
    shutil.copy(src_path, dest_path)
    return dest_path


def _ensure_audio_local(entry: Dict) -> bool:
    rel_path = entry.get('audio_path')
    if not rel_path:
        return False
    audio_path = Path(rel_path)
    if not audio_path.is_absolute():
        audio_path = REPO_ROOT / audio_path
    try:
        resolved = audio_path.resolve()
    except FileNotFoundError:
        return False
    if HISTORY_DIR.resolve() in resolved.parents:
        return False
    if not audio_path.exists():
        return False
    dest = _copy_audio_to_history(audio_path, entry.get('id'), entry.get('timestamp'))
    if dest:
        entry['audio_path'] = _repo_relative(dest)
        return True
    return False


def _ensure_demo_chat(entry: Dict) -> bool:
    if entry.get('chat_history'):
        return False
    meta = entry.get('metadata', {})
    demo_id = meta.get('demo_id')
    if not demo_id:
        entry_id = entry.get('id', '')
        if entry_id.startswith('demo_'):
            demo_id = entry_id.split('demo_', 1)[1]
    if not demo_id:
        return False
    dialog_path = Path(DEMO_DIALOG_DIR) / f'{demo_id}.txt'
    if not dialog_path.exists():
        return False
    chat_history = _parse_demo_dialog(dialog_path)
    if not chat_history:
        return False
    entry['chat_history'] = chat_history
    return True
