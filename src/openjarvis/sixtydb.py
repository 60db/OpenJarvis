"""60db platform requests, shared by speech, setup, and Judge."""

from __future__ import annotations

import os
from typing import Any

import httpx

API_BASE = "https://api.60db.ai"
CHAT_MODEL = "60db-tiny"


def api_key() -> str:
    from openjarvis.core.credentials import get_tool_credential

    return (
        os.environ.get("SIXTYDB_API_KEY")
        or get_tool_credential("sixtydb", "SIXTYDB_API_KEY")
        or ""
    )


def request(method: str, path: str, *, key: str = "", **kwargs: Any) -> httpx.Response:
    key = key or api_key()
    if not key:
        raise ValueError("Add your 60db API key in Settings to continue.")
    try:
        response = httpx.request(
            method,
            f"{API_BASE}{path}",
            headers={"Authorization": f"Bearer {key}"},
            timeout=120,
            **kwargs,
        )
    except httpx.RequestError as exc:
        raise RuntimeError("Could not connect to 60db. Try again shortly.") from exc
    if not response.is_success:
        messages = {
            401: "Invalid 60db API key.",
            402: "Your 60db balance is insufficient.",
            403: "Your 60db key does not have permission for this service.",
            429: "60db is busy. Try again shortly.",
        }
        raise RuntimeError(
            messages.get(
                response.status_code,
                f"60db request failed (HTTP {response.status_code}).",
            )
        )
    return response


def voices(*, key: str = "") -> list[dict[str, Any]]:
    catalog = request("GET", "/voices", key=key).json()
    if catalog.get("success") is False:
        raise RuntimeError("60db could not load the voice catalog.")
    return catalog["data"]


def evaluate(state: Any, questions: dict[str, Any]) -> dict[str, Any]:
    if not questions or len(questions) > 32:
        raise ValueError("Judge requires between 1 and 32 questions.")
    return request(
        "POST",
        "/v1/systemone",
        json={
            "state": state,
            "questions": questions,
        },
    ).json()
