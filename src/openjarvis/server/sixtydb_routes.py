"""Local 60db setup and decision-model API."""

from __future__ import annotations

import asyncio
import ipaddress
import os
import threading
from typing import Any

import tomlkit
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr

from openjarvis import sixtydb
from openjarvis.core.config import load_config
from openjarvis.core.paths import get_config_path

router = APIRouter(prefix="/v1/sixtydb", tags=["60db"])
_config_lock = threading.Lock()


class KeyRequest(BaseModel):
    api_key: SecretStr = SecretStr("")


class SetupRequest(KeyRequest):
    voice_id: str = Field(min_length=1, max_length=200)
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)


class JudgeRequest(BaseModel):
    state: str | dict[str, Any] | list[Any]
    questions: dict[str, Any] = Field(min_length=1, max_length=32)


def _authorize_setup(request: Request) -> None:
    # A remotely exposed, keyless server must not accept credential changes.
    if getattr(request.app.state, "api_key", ""):
        return  # AuthMiddleware already checked the token.
    try:
        local = bool(
            request.client and ipaddress.ip_address(request.client.host).is_loopback
        )
    except ValueError:
        local = False
    if not local:
        raise HTTPException(
            403, "Configure 60db from this computer or authenticate the server."
        )


def _key(body: KeyRequest) -> str:
    value = body.api_key.get_secret_value().strip() or sixtydb.api_key()
    if not value or len(value) > 4096 or any(c.isspace() for c in value):
        raise HTTPException(400, "Enter a valid 60db API key.")
    return value


def configure(key: str, voice_id: str, speed: float) -> None:
    from openjarvis.core.credentials import save_credential
    from openjarvis.security.file_utils import secure_write_text

    path = get_config_path()
    if os.environ.get("OPENJARVIS_CONFIG"):
        from pathlib import Path

        path = Path(os.environ["OPENJARVIS_CONFIG"]).expanduser()
    with _config_lock:
        original = path.read_text() if path.exists() else ""
        doc = tomlkit.parse(original)
        values = {
            "engine": {"default": "sixtydb"},
            "intelligence": {
                "default_model": sixtydb.CHAT_MODEL,
                "preferred_engine": "sixtydb",
                "provider": "sixtydb",
                "fallback_model": "",
                "model_chat": sixtydb.CHAT_MODEL,
                "model_short": sixtydb.CHAT_MODEL,
                "model_long": sixtydb.CHAT_MODEL,
                "model_code": sixtydb.CHAT_MODEL,
            },
            "server": {"model": sixtydb.CHAT_MODEL},
            "deep_research": {"engine": "sixtydb", "model": sixtydb.CHAT_MODEL},
            "spec_search": {
                "teacher_engine": "sixtydb",
                "teacher_model": sixtydb.CHAT_MODEL,
            },
            "optimize": {
                "optimizer_provider": "sixtydb",
                "optimizer_model": sixtydb.CHAT_MODEL,
                "judge_model": sixtydb.CHAT_MODEL,
            },
            "speech": {
                "backend": "sixtydb",
                "tts_backend": "sixtydb",
                "voice_id": voice_id,
                "voice_speed": speed,
            },
            "digest": {"tts_backend": "sixtydb", "voice_id": voice_id},
        }
        for section, fields in values.items():
            if section not in doc:
                doc[section] = tomlkit.table()
            doc[section].update(fields)
        secure_write_text(path, tomlkit.dumps(doc), mode=0o600)
        try:
            save_credential("sixtydb", "SIXTYDB_API_KEY", key)
        except Exception:
            secure_write_text(path, original, mode=0o600)
            raise
        load_config.cache_clear()


def refresh_runtime(app) -> None:
    """Refresh credentials through existing wrappers so agents retain guardrails."""
    from openjarvis.engine.sixtydb import SixtyDBEngine
    from openjarvis.speech.sixtydb import SixtyDBSpeechBackend

    engine = app.state.engine
    while hasattr(engine, "_inner") or hasattr(engine, "_engine"):
        engine = getattr(engine, "_inner", None) or engine._engine
    if isinstance(engine, SixtyDBEngine):
        engine.set_api_key(sixtydb.api_key())
    else:
        raise RuntimeError("Restart Jarvis with --engine sixtydb to apply this setup.")
    app.state.config = load_config()
    app.state.model = sixtydb.CHAT_MODEL
    app.state.speech_backend = SixtyDBSpeechBackend()
    app.state.tts_resolved = False
    app.state.tts_backend = None


@router.get("/status")
def status(request: Request):
    cfg = getattr(request.app.state, "config", None) or load_config()
    return {
        "key_configured": bool(sixtydb.api_key()),
        "voice_id": cfg.speech.voice_id,
        "voice_speed": cfg.speech.voice_speed,
        "model": sixtydb.CHAT_MODEL,
    }


@router.post("/voices")
async def voice_catalog(body: KeyRequest, request: Request):
    _authorize_setup(request)
    try:
        return {"voices": await asyncio.to_thread(sixtydb.voices, key=_key(body))}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/configure")
async def setup(body: SetupRequest, request: Request):
    _authorize_setup(request)
    key = _key(body)
    try:
        catalog = await asyncio.to_thread(sixtydb.voices, key=key)
        if body.voice_id not in {v["voice_id"] for v in catalog}:
            raise HTTPException(400, "Choose a voice from your 60db voice catalog.")
        await asyncio.to_thread(configure, key, body.voice_id, body.voice_speed)
        refresh_runtime(request.app)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
    return status(request)


@router.post("/judge")
async def judge(body: JudgeRequest):
    try:
        return await asyncio.to_thread(sixtydb.evaluate, body.state, body.questions)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
