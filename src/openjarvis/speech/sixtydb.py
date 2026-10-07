"""60db Garuda transcription and Kaak speech synthesis."""

from __future__ import annotations

import base64
import io
import wave

from openjarvis import sixtydb
from openjarvis.core.registry import SpeechRegistry, TTSRegistry
from openjarvis.speech._stubs import Segment, SpeechBackend, TranscriptionResult
from openjarvis.speech.tts import TTSBackend, TTSResult


@SpeechRegistry.register("sixtydb")
class SixtyDBSpeechBackend(SpeechBackend):
    backend_id = "sixtydb"

    def transcribe(self, audio: bytes, *, format: str = "wav", language=None):
        format = format.lower().lstrip(".")
        if format not in self.supported_formats():
            raise ValueError("Unsupported audio format for 60db transcription.")
        if not audio or len(audio) > 10 * 1024 * 1024:
            raise ValueError("Audio must be non-empty and at most 10 MB.")
        data = {"language": language} if language and language != "auto" else {}
        mime = {"mp3": "audio/mpeg", "m4a": "audio/mp4", "mp4": "audio/mp4"}.get(
            format, f"audio/{format}"
        )
        result = sixtydb.request(
            "POST",
            "/stt",
            files={"file": (f"audio.{format}", audio, mime)},
            data=data,
        ).json()
        return TranscriptionResult(
            text=result["text"],
            language=result.get("language"),
            duration_seconds=result.get("duration_sec", 0),
            segments=[
                Segment(
                    text=s["text"],
                    start=s["start"],
                    end=s["end"],
                    confidence=s.get("confidence"),
                )
                for s in result.get("segments", [])
            ],
        )

    def health(self) -> bool:
        return bool(sixtydb.api_key())

    def supported_formats(self) -> list[str]:
        return ["wav", "mp3", "m4a", "ogg", "flac", "webm", "mp4"]


@TTSRegistry.register("sixtydb")
class SixtyDBTTSBackend(TTSBackend):
    backend_id = "sixtydb"

    def synthesize(self, text, *, voice_id="", speed=1.0, output_format="wav"):
        text = text.replace("**", "").strip()
        if not text.strip() or len(text) > 5000:
            raise ValueError("Speech text must contain 1–5000 characters.")
        if not 0.5 <= speed <= 2:
            raise ValueError("Speech speed must be between 0.5 and 2.")
        if not voice_id:
            from openjarvis.core.config import load_config

            voice_id = load_config().speech.voice_id
        if not voice_id:
            raise ValueError("Choose a 60db voice in Settings first.")
        data = sixtydb.request(
            "POST",
            "/tts-synthesize",
            json={
                "text": text,
                "voice_id": voice_id,
                "speed": speed,
                "audio_config": {
                    "audio_encoding": "LINEAR16",
                    "sample_rate_hertz": 24000,
                },
                "timestamp_type": "NONE",
            },
        ).json()
        if data.get("success") is False:
            raise RuntimeError("60db could not synthesize speech.")
        encoded = data.get("audio_base64") or data.get("audioContent")
        if not isinstance(encoded, str) or not encoded:
            raise RuntimeError("60db returned no audio content.")
        audio = base64.b64decode(encoded, validate=True)
        sample_rate = int(data.get("sample_rate", 24000))
        encoding = str(data.get("encoding", "LINEAR16")).lower()
        if not audio:
            raise RuntimeError("60db returned empty audio.")
        if audio.startswith(b"RIFF"):
            format = "wav"
        elif encoding in {"linear16", "pcm", "pcm_s16le"}:
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(audio)
            audio, format = buffer.getvalue(), "wav"
        else:
            format = (
                "ogg"
                if audio.startswith(b"OggS")
                else data.get("output_format", encoding)
            )
            if format not in {"mp3", "ogg", "wav"}:
                raise RuntimeError("60db returned an unsupported audio encoding.")
        return TTSResult(
            audio=audio,
            format=format,
            voice_id=voice_id,
            sample_rate=sample_rate,
            duration_seconds=data.get("duration_seconds", 0),
        )

    def available_voices(self) -> list[str]:
        return [v["voice_id"] for v in sixtydb.voices()]

    def health(self) -> bool:
        return bool(sixtydb.api_key())
