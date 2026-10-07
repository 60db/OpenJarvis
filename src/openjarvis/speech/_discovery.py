"""Resolve 60db transcription without provider fallback."""

from openjarvis.speech.sixtydb import SixtyDBSpeechBackend


def get_speech_backend(config):
    backend = SixtyDBSpeechBackend()
    return backend if backend.health() else None
