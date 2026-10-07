"""60db wire contracts and the one-key setup-to-chat flow; no paid API calls."""

import asyncio
import base64
import io
import json
import wave

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from openjarvis import sixtydb
from openjarvis.core.config import JarvisConfig, load_config
from openjarvis.core.credentials import inject_credentials
from openjarvis.core.registry import TTSRegistry
from openjarvis.core.types import Message, Role, Trace
from openjarvis.engine.sixtydb import SixtyDBEngine
from openjarvis.learning.optimize.feedback.judge import TraceJudge
from openjarvis.server.api_routes import speech_router
from openjarvis.server.routes import router as chat_router
from openjarvis.server.sixtydb_routes import router as setup_router
from openjarvis.speech.sixtydb import SixtyDBSpeechBackend, SixtyDBTTSBackend


def test_setup_chat_speech_and_judge(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENJARVIS_HOME", str(tmp_path))
    monkeypatch.delenv("SIXTYDB_API_KEY", raising=False)
    load_config.cache_clear()
    calls = []
    pcm = b"\x01\x00" * 240

    def platform_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        assert url.startswith("https://api.60db.ai/")
        assert kwargs["headers"]["Authorization"] == "Bearer sk-test"
        payloads = {
            "/voices": {"data": [{"voice_id": "voice-hi", "name": "Hindi"}]},
            "/stt": {"text": "नमस्ते", "language": "hi", "duration_sec": 1.2},
            "/tts-synthesize": {
                "audio_base64": base64.b64encode(pcm).decode(),
                "sample_rate": 24000,
                "encoding": "LINEAR16",
            },
            "/v1/systemone": {
                "answers": {"quality": {"score": 2.4, "confidence": 0.9}}
            },
        }
        return httpx.Response(200, json=payloads[httpx.URL(url).path])

    monkeypatch.setattr(httpx, "request", platform_request)
    engine = SixtyDBEngine()
    app = FastAPI()
    app.state.engine = engine
    app.state.engine_name = "sixtydb"
    app.state.config = JarvisConfig()
    app.state.api_key = ""
    app.state.speech_backend = None
    app.include_router(setup_router)
    app.include_router(speech_router)
    app.include_router(chat_router)
    TTSRegistry.register_value("sixtydb", SixtyDBTTSBackend)
    client = TestClient(app, client=("127.0.0.1", 12345))
    assert client.get("/v1/sixtydb/status").json()["key_configured"] is False
    assert (
        client.post("/v1/sixtydb/voices", json={"api_key": "sk-test"}).status_code
        == 200
    )
    assert (
        client.post(
            "/v1/sixtydb/configure",
            json={
                "api_key": "sk-test",
                "voice_id": "other-workspace",
            },
        ).status_code
        == 400
    )
    assert not (tmp_path / "credentials.toml").exists()
    response = client.post(
        "/v1/sixtydb/configure",
        json={
            "api_key": "sk-test",
            "voice_id": "voice-hi",
        },
    )
    assert response.status_code == 200
    assert "sk-test" not in response.text
    config = load_config()
    assert config.engine.default == "sixtydb"
    assert config.speech.voice_id == "voice-hi"
    assert config.digest.voice_id == "voice-hi"
    assert "sk-test" not in (tmp_path / "config.toml").read_text()
    assert (tmp_path / "credentials.toml").stat().st_mode & 0o777 == 0o600
    monkeypatch.delenv("SIXTYDB_API_KEY")
    inject_credentials()
    assert engine.health()

    def chat_response(request):
        assert request.url == "https://api.60db.ai/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer sk-test"
        assert json.loads(request.content)["save_chat"] is False
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"content": "Hello"},
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    engine._client.close()
    engine._client = httpx.Client(
        base_url=sixtydb.API_BASE,
        headers=engine._headers,
        transport=httpx.MockTransport(chat_response),
    )
    chat = client.post(
        "/v1/chat/completions",
        json={
            "model": "60db-tiny",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    assert chat.status_code == 200
    assert chat.json()["choices"][0]["message"]["content"] == "Hello"
    assert (
        client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        ).status_code
        == 400
    )
    transcription = client.post(
        "/v1/speech/transcribe",
        files={
            "file": ("audio.webm", b"fake-audio", "audio/webm"),
        },
    )
    assert transcription.json()["text"] == "नमस्ते"
    assert "language" not in next(k for _, u, k in calls if u.endswith("/stt"))["data"]
    audio = client.post("/v1/speech/synthesize", json={"text": "**नमस्ते**"})
    assert audio.status_code == 200
    assert next(k for _, u, k in calls if u.endswith("/tts-synthesize"))["json"][
        "text"
    ] == "नमस्ते"
    assert audio.headers["content-type"] == "audio/wav"
    with wave.open(io.BytesIO(audio.content)) as wav:
        assert wav.getframerate() == 24000
        assert wav.readframes(240) == pcm
    result = client.post(
        "/v1/sixtydb/judge",
        json={
            "state": {"query": "Hello", "answer": "Hello"},
            "questions": {"quality": {"type": "score", "criteria": ["Bad", "Good"]}},
        },
    )
    assert result.json()["answers"]["quality"]["score"] == 2.4
    score, _ = TraceJudge(None, "60db-tiny").score_trace(
        Trace(query="Hello", result="Hello")
    )
    assert score == pytest.approx(0.8)
    engine.close()
    load_config.cache_clear()


def test_chat_stream_and_tools_use_60db_contract():
    seen = []
    chunks = [
        {"type": "chat_id", "chat_id": "unused"},
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [], "usage": {"completion_tokens": 1}},
        {"type": "done"},
    ]

    def transport(request):
        payload = json.loads(request.content)
        seen.append(payload)
        assert "tools" not in payload and "tool_choice" not in payload
        assert payload["tool"][0]["name"] == "calculator"
        events = "".join(f"data: {json.dumps(c)}\n\n" for c in chunks)
        return httpx.Response(200, text=events + "data: [DONE]\n\n")

    engine = SixtyDBEngine(api_key="sk-test")
    engine._async_transport = httpx.MockTransport(transport)
    messages = [Message(role=Role.USER, content="Hello")]
    tools = [{"type": "function", "function": {"name": "calculator", "parameters": {}}}]

    async def check():
        tokens = [
            t async for t in engine.stream(messages, model="60db-tiny", tools=tools)
        ]
        assert tokens == ["Hello"]
        rich = [
            t
            async for t in engine.stream_full(messages, model="60db-tiny", tools=tools)
        ]
        assert rich[0].content == "Hello"
        assert rich[1].usage == {"completion_tokens": 1}
        await engine._async_client.aclose()

    asyncio.run(check())
    engine.close()
    assert len(seen) == 2


def test_missing_key_and_speech_limits(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENJARVIS_HOME", str(tmp_path))
    monkeypatch.delenv("SIXTYDB_API_KEY", raising=False)
    engine = SixtyDBEngine()
    assert engine.health() is False
    with pytest.raises(ValueError, match="API key"):
        engine.generate([], model="60db-tiny")
    with pytest.raises(ValueError, match="10 MB"):
        SixtyDBSpeechBackend().transcribe(b"x" * (10 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="speed"):
        SixtyDBTTSBackend().synthesize("Hello", voice_id="v", speed=0)
    engine.close()


def test_remote_keyless_setup_is_rejected():
    app = FastAPI()
    app.state.api_key = ""
    app.include_router(setup_router)
    response = TestClient(app, client=("203.0.113.1", 12345)).post(
        "/v1/sixtydb/voices",
        json={"api_key": "sk-test"},
    )
    assert response.status_code == 403


def test_microphone_upload_uses_audio_mime(monkeypatch):
    def provider(method, url, **kwargs):
        upload = kwargs["files"]["file"]
        accepted = len(upload) == 3 and upload[2] == "audio/webm"
        return httpx.Response(200 if accepted else 400, json={"text": "Hello"})

    monkeypatch.setenv("SIXTYDB_API_KEY", "sk-test")
    monkeypatch.setattr(httpx, "request", provider)
    assert (
        SixtyDBSpeechBackend().transcribe(b"webm-fixture", format="webm").text
        == "Hello"
    )


def test_tts_accepts_live_audio_content_response(monkeypatch):
    pcm = b"\x01\x00" * 240
    monkeypatch.setenv("SIXTYDB_API_KEY", "sk-test")
    monkeypatch.setattr(
        httpx,
        "request",
        lambda *args, **kwargs: httpx.Response(
            200,
            json={"audioContent": base64.b64encode(pcm).decode(), "conditioning": {}},
        ),
    )
    result = SixtyDBTTSBackend().synthesize("Hello", voice_id="voice-hi")
    assert result.format == "wav"
    with wave.open(io.BytesIO(result.audio)) as wav:
        assert wav.getframerate() == 24000
        assert wav.readframes(240) == pcm


@pytest.mark.parametrize(
    ("text", "spoken"),
    [
        (
            "Here is **important text** and **नमस्ते**.",
            "Here is important text and नमस्ते.",
        ),
        ("**First line\nsecond line**", "First line\nsecond line"),
        ("  Already plain: 2 * 3 = 6.  ", "Already plain: 2 * 3 = 6."),
        ("**", ""),
    ],
)
def test_tts_does_not_send_bold_markers(monkeypatch, text, spoken):
    sent = []

    def provider(*args, **kwargs):
        sent.append(kwargs["json"]["text"])
        return httpx.Response(
            200, json={"audioContent": base64.b64encode(b"\x01\x00" * 240).decode()}
        )

    monkeypatch.setenv("SIXTYDB_API_KEY", "sk-test")
    monkeypatch.setattr(httpx, "request", provider)
    backend = SixtyDBTTSBackend()
    if spoken:
        backend.synthesize(text, voice_id="voice-hi")
        assert sent == [spoken]
    else:
        with pytest.raises(ValueError, match="1–5000"):
            backend.synthesize(text, voice_id="voice-hi")
        assert sent == []
