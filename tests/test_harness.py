import pytest

from agent_platform import AgentHarness, AgentManifest, AgentRegistry, RunRequest
from agent_platform.manifest import BudgetSpec
from agent_platform.policy import PolicyEngine
from agent_platform.telemetry import InMemoryTelemetry
from agent_platform.tools import ToolRegistry


def setup_harness(manifest, tool=lambda text: text):
    registry = AgentRegistry()
    registry.register(manifest)
    tools = ToolRegistry()
    tools.add("echo", tool)
    telemetry = InMemoryTelemetry()
    return AgentHarness(registry, tools, PolicyEngine(), telemetry), telemetry


def make_manifest(**kw):
    return AgentManifest(agent_id="agent-1", owner="team-a", purpose="Echo tasks", **kw)


def test_allowed_tool_completes_and_emits_events():
    harness, telemetry = setup_harness(make_manifest(allowed_tools=["echo"]))
    result = harness.run(RunRequest("agent-1", "echo", "echo", {"text": "hello"}))
    assert result.status == "completed"
    assert result.output == "hello"
    assert [e.name for e in telemetry.events] == ["agent.run.started", "agent.run.completed"]


def test_events_share_trace_id_and_have_span_ids():
    harness, telemetry = setup_harness(make_manifest(allowed_tools=["echo"]))
    harness.run(RunRequest("agent-1", "echo", "echo", {"text": "hi"}, trace_id="t-1"))
    assert {e.attributes["trace_id"] for e in telemetry.events} == {"t-1"}
    assert all(e.attributes["span_id"] for e in telemetry.events)


def test_unauthorized_tool_is_blocked_before_dispatch():
    harness, telemetry = setup_harness(make_manifest())
    result = harness.run(RunRequest("agent-1", "echo", "echo", {"text": "hello"}))
    assert result.status == "blocked"
    assert result.reason == "tool_not_allowed:echo"
    assert result.usage.steps == 0
    assert telemetry.events[-1].name == "agent.run.blocked"


def test_budget_exhaustion_terminates_run():
    manifest = make_manifest(allowed_tools=["echo"],
                             budget=BudgetSpec(max_steps=1, max_tokens=10, max_cost_usd=0.01))
    harness, telemetry = setup_harness(manifest)
    result = harness.run(RunRequest("agent-1", "echo", "echo", {"text": "hello"},
                                    estimated_tokens=100))
    assert result.status == "terminated"
    assert result.reason == "maximum tokens exceeded"
    assert telemetry.events[-1].name == "agent.run.terminated"


def test_tool_error_is_reported_as_failed():
    def boom(text):
        raise RuntimeError("tool down")

    harness, telemetry = setup_harness(make_manifest(allowed_tools=["echo"]), tool=boom)
    result = harness.run(RunRequest("agent-1", "echo", "echo", {"text": "x"}))
    assert result.status == "failed"
    assert telemetry.counts()["agent.run.failed"] == 1


def test_unknown_agent_is_rejected():
    harness, _ = setup_harness(make_manifest())
    with pytest.raises(KeyError):
        harness.run(RunRequest("nope", "echo", "echo", {}))
