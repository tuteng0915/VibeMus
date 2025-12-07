"""FastAPI backend server for VibeMus.

Provides REST endpoints so the system can run as a pure backend service
without the Gradio UI. Keeps parity with the UI logic wherever possible.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from assistant import assistant
from history import (
    ensure_history_storage,
    find_history_entry_by_display,
    find_history_entry_by_id,
    log_audio_snapshot,
    read_history_entries,
    seed_default_demo_history,
    seed_outputs_history,
)
from pipeline import pipe

app = FastAPI(
    title="VibeMus Backend",
    version="1.0.0",
    description="LLM-powered music generation backend",
)


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    preference: str = ""
    lyrics: str = ""
    tags: str = ""
    path: str = ""
    nickname: Optional[str] = None


class GenerateRequest(BaseModel):
    lyrics: str
    tags: str
    length: float = 60.0
    nickname: Optional[str] = None


class HistorySelection(BaseModel):
    display: str


def _log_if_needed(path, lyrics, tags, previous_path=None, duration=None, nickname=None, chat_history=None):
    if not path or path in ('', 'blank.wav'):
        return None
    if previous_path and previous_path == path:
        return None
    return log_audio_snapshot(path, lyrics, tags, duration=duration, nickname=nickname, chat_history=chat_history)


def _assistant_chat(req: ChatRequest):
    var_dict = {
        'preference': req.preference,
        'lyrics': req.lyrics,
        'tags': req.tags,
        'path': req.path,
    }
    messages = list(req.history)
    messages.append({'role': 'user', 'content': req.message})
    response = assistant.run_nonstream(messages=messages, var_dict=var_dict)
    entry = _log_if_needed(
        var_dict['path'],
        var_dict['lyrics'],
        var_dict['tags'],
        previous_path=req.path,
        nickname=req.nickname,
        chat_history=messages + [{'role': 'assistant', 'content': response}],
    )
    return response, var_dict, entry


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    response, var_dict, entry = _assistant_chat(req)
    return {
        'response': response,
        'lyrics': var_dict['lyrics'],
        'tags': var_dict['tags'],
        'audio_path': var_dict['path'],
        'history_entry': entry,
        'history_dropdown': [entry['display'] for entry in reversed(read_history_entries())],
    }


@app.post("/api/generate")
def generate_endpoint(req: GenerateRequest):
    outputs = pipe(
        format='wav',
        audio_duration=req.length,
        prompt=req.tags,
        lyrics=req.lyrics,
    )
    entry = log_audio_snapshot(outputs[0], req.lyrics, req.tags, duration=req.length, nickname=req.nickname)
    return {
        'audio_path': outputs[0],
        'history_entry': entry,
    }


@app.get("/api/history")
def list_history():
    return {
        'entries': read_history_entries()
    }


@app.get("/api/history/{entry_id}")
def get_history_entry(entry_id: str):
    entry = find_history_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    return entry


@app.get("/api/history/{entry_id}/audio")
def download_history_audio(entry_id: str):
    entry = find_history_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    audio_path = entry['audio_path']
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file missing")
    filename = os.path.basename(audio_path)
    return FileResponse(audio_path, filename=filename, media_type='audio/wav')


@app.post("/api/history/load")
def load_history_entry(selection: HistorySelection):
    entry = find_history_entry_by_display(selection.display)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    return entry


ensure_history_storage()
seed_default_demo_history()
seed_outputs_history()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
