"""60db Vyas chat, using the existing OpenAI wire-protocol engine."""

from __future__ import annotations

from typing import Any

from openjarvis import sixtydb
from openjarvis.core.registry import EngineRegistry
from openjarvis.engine._openai_compat import _OpenAICompatibleEngine


@EngineRegistry.register("sixtydb")
class SixtyDBEngine(_OpenAICompatibleEngine):
    engine_id = "sixtydb"
    is_cloud = True
    _default_host = sixtydb.API_BASE

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            api_key=kwargs.pop("api_key", None) or sixtydb.api_key(), **kwargs
        )

    def _prepare_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise ValueError("Add your 60db API key in Settings to continue.")
        if payload.get("model") != sixtydb.CHAT_MODEL:
            raise ValueError("Choose the 60db chat model: 60db-tiny.")
        if "tools" in payload:
            payload["tool"] = [
                tool.get("function", tool) for tool in payload.pop("tools")
            ]
            payload.pop("tool_choice", None)
        payload["save_chat"] = False
        return payload

    def list_models(self) -> list[str]:
        # The chat reference documents this model; /v1/models is not required.
        return [sixtydb.CHAT_MODEL]

    def can_serve(self, model: str) -> bool:
        return model in self.list_models()

    def health(self) -> bool:
        return bool(self._api_key)

    def set_api_key(self, key: str) -> None:
        self._api_key = key or None
        self._headers = {"Authorization": f"Bearer {key}"} if key else {}
        self._client.headers.pop("Authorization", None)
        self._client.headers.update(self._headers)
        if self._async_client is not None:
            self._async_client.headers.pop("Authorization", None)
            self._async_client.headers.update(self._headers)
