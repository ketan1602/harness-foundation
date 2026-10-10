from unittest.mock import AsyncMock, MagicMock

import pytest
from run_llm_demo import build_llm_harness

from agent_platform import RunRequest
from agent_platform.llm import LLM, make_llm


def fake_client(answer="outage", tokens=123):
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=answer))],
                               usage=MagicMock(total_tokens=tokens)))
    return client


def setup_llm(client):
    return build_llm_harness(LLM(client, "m"))


def test_llm_call_runs_through_harness():
    harness, telemetry = build_llm_harness(LLM(fake_client(), "m"))
    result = harness.run(RunRequest("triage-agent", "t", "classify_ticket", {"text": "down"}))
    assert (result.status, result.output) == ("completed", "outage")
    assert telemetry.counts()["agent.run.completed"] == 1


def test_measured_tokens_replace_the_estimate():
    harness, _ = setup_llm(fake_client(tokens=123))
    result = harness.run(RunRequest("triage-agent", "t", "classify_ticket", {"text": "x"},
                                    estimated_tokens=800))
    assert result.usage.tokens == 123


def test_measured_overrun_terminates_run():
    harness, telemetry = setup_llm(fake_client(tokens=9000))
    result = harness.run(RunRequest("triage-agent", "t", "classify_ticket", {"text": "x"},
                                    estimated_tokens=800))
    assert (result.status, result.reason) == ("terminated", "maximum tokens exceeded")
    assert telemetry.events[-1].name == "agent.run.terminated"


def test_missing_api_key_fails_loudly(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="LLM_CLIENT"):
        make_llm()


def test_client_loaded_from_env(monkeypatch):
    monkeypatch.setenv("LLM_CLIENT", "unittest.mock:MagicMock")
    monkeypatch.setenv("LLM_API_KEY", "k")
    monkeypatch.setenv("LLM_MODEL", "m")
    assert make_llm()._model == "m"
