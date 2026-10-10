"""Same ticket, two paths: the direct call has no policy, budget, trace or result envelope."""
from _setup import build_harness, create_ticket, show

from agent_platform import RunRequest

direct = create_ticket(subject="Service unavailable", priority="high")
print("direct:", direct)

harness, telemetry = build_harness()
harnessed = harness.run(RunRequest(
    agent_id="support-agent",
    task="Create a support ticket",
    tool_name="create_ticket",
    tool_args={"subject": "Service unavailable", "priority": "high"},
))
show(harnessed, telemetry)
