"""The three experiments produce the documented outcomes."""
from _setup import build_harness

from agent_platform import RunRequest


def run(tool, args, **kw):
    harness, telemetry = build_harness()
    return harness.run(RunRequest("support-agent", "task", tool, args, **kw)), telemetry


def test_experiment_1_harnessed_ticket_completes():
    result, telemetry = run("create_ticket", {"subject": "s", "priority": "high"})
    assert result.status == "completed"
    assert result.output["ticket_id"] == "T-1001"
    assert telemetry.counts()["agent.run.completed"] == 1


def test_experiment_2_delete_customer_blocked():
    result, _ = run("delete_customer", {"customer_id": "C-42"})
    assert (result.status, result.reason) == ("blocked", "tool_not_allowed:delete_customer")
    assert result.usage.steps == 0


def test_experiment_3_token_ceiling_terminates():
    result, telemetry = run("create_ticket", {"subject": "s", "priority": "high"},
                            estimated_tokens=6000)
    assert (result.status, result.reason) == ("terminated", "maximum tokens exceeded")
    assert telemetry.events[-1].name == "agent.run.terminated"


def test_exp1_direct_path_has_no_policy_or_budget():
    from exp1_direct_vs_harnessed import compare
    _, unauthorized, oversized = compare()
    assert unauthorized[1].startswith("ran:")
    assert unauthorized[2].startswith("blocked")
    assert oversized[1].startswith("ran:")
    assert oversized[2].startswith("terminated")


def test_registry_demo_lists_agents_by_owner():
    from registry_demo import build_registry
    ids = [m.agent_id for m in build_registry().by_owner("customer-platform")]
    assert ids == ["support-agent", "triage-agent"]
