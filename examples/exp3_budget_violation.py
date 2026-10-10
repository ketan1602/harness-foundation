"""A request estimated above the 5000-token ceiling is terminated before the tool runs."""
from _setup import build_harness, show

from agent_platform import RunRequest

harness, telemetry = build_harness()
result = harness.run(RunRequest(
    agent_id="support-agent",
    task="Create a ticket with a very large context",
    tool_name="create_ticket",
    tool_args={"subject": "Service unavailable", "priority": "high"},
    estimated_tokens=6000,
))
show(result, telemetry)
