"""Inference Engine primitive — LLM runtime management."""

from __future__ import annotations

# Daily-use inference uses only 60db.
import openjarvis.engine.sixtydb  # noqa: F401
from openjarvis.engine._base import (
    EngineConnectionError,
    EngineContextLengthError,
    InferenceEngine,
    looks_like_context_length_error,
    messages_to_dicts,
)
from openjarvis.engine._discovery import discover_engines, discover_models, get_engine

__all__ = [
    "EngineConnectionError",
    "EngineContextLengthError",
    "InferenceEngine",
    "discover_engines",
    "discover_models",
    "get_engine",
    "looks_like_context_length_error",
    "messages_to_dicts",
]
