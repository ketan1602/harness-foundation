from _setup import build_harness, show

from agent_platform import RunRequest

harness, telemetry = build_harness()
result = harness.run(RunRequest(
    agent_id="support-agent",
    task="Create a high-priority ticket for unavailable service",
    tool_name="create_ticket",
    tool_args={"subject": "Service unavailable", "priority": "high"},
))
show(result, telemetry)
