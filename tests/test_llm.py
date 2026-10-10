from unittest.mock import AsyncMock, MagicMock

import pytest
from run_llm_demo import build_llm_harness

from agent_platform import RunRequest
from agent_platform.llm import LLM, make_llm


def fake_client(answer="outage"):
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=answer))]))
    return client


def test_llm_call_runs_through_harness():
    harness, telemetry = build_llm_harness(LLM(fake_client(), "m"))
    result = harness.run(RunRequest("triage-agent", "t", "classify_ticket", {"text": "down"}))
    assert (result.status, result.output) == ("completed", "outage")
    assert telemetry.counts()["agent.run.completed"] == 1


def test_missing_api_key_fails_loudly(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="LLM_CLIENT"):
        make_llm()


def test_client_loaded_from_env(monkeypatch):
    monkeypatch.setenv("LLM_CLIENT", "unittest.mock:MagicMock")
    monkeypatch.setenv("LLM_API_KEY", "k")
    monkeypatch.setenv("LLM_MODEL", "m")
    assert make_llm()._model == "m"
