"""Generic async chat-completions client (OpenAI-compatible), fully selected by env vars.

LLM_CLIENT   dotted path "module:Class" of an async client exposing chat.completions.create
LLM_API_KEY  credential passed to the client
LLM_MODEL    model name
LLM_USE_TRUSTSTORE  optional "1" to use the OS trust store for TLS
"""
import asyncio
import os
from importlib import import_module


class LLM:
    def __init__(self, client, model: str) -> None:
        self._client = client
        self._model = model

    async def achat(self, system: str, user: str) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content

    def chat(self, system: str, user: str) -> str:
        """Sync entry point so the (sync) harness can mediate LLM calls as tools."""
        return asyncio.run(self.achat(system, user))


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"{name} must be set (see .env.example)")
    return value


def make_llm() -> LLM:
    client_path, api_key, model = _required("LLM_CLIENT"), _required("LLM_API_KEY"), \
        _required("LLM_MODEL")
    if os.environ.get("LLM_USE_TRUSTSTORE") == "1":
        import truststore
        truststore.inject_into_ssl()
    module_name, _, class_name = client_path.partition(":")
    client_cls = getattr(import_module(module_name), class_name)
    return LLM(client_cls(api_key=api_key), model)
