"""delete_customer exists as a tool but is not in the manifest: blocked, zero invocations."""
from _setup import build_harness, show

from agent_platform import RunRequest

harness, telemetry = build_harness()
result = harness.run(RunRequest(
    agent_id="support-agent",
    task="Remove a customer",
    tool_name="delete_customer",
    tool_args={"customer_id": "C-42"},
))
show(result, telemetry)
