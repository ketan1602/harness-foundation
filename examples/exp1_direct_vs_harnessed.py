"""Same three requests, two paths: direct tool calls versus the harness."""
from _setup import build_harness, create_ticket, delete_customer

from agent_platform import RunRequest

TICKET = {"subject": "Service unavailable", "priority": "high"}


def _direct(tool, args):
    try:
        return f"ran: {tool(**args)}"
    except Exception as exc:  # noqa: BLE001 - direct path has no failure handling to compare
        return f"raised {type(exc).__name__}"


def _harnessed(tool_name, args, **kw):
    harness, telemetry = build_harness()
    result = harness.run(RunRequest("support-agent", "task", tool_name, args, **kw))
    return f"{result.status} ({result.reason or 'ok'}), events={len(telemetry.events)}"


def compare() -> list[tuple[str, str, str]]:
    return [
        ("Normal ticket", _direct(create_ticket, TICKET),
         _harnessed("create_ticket", TICKET)),
        ("Unauthorized delete_customer", _direct(delete_customer, {"customer_id": "C-42"}),
         _harnessed("delete_customer", {"customer_id": "C-42"})),
        ("Oversized request (6000 tokens)", _direct(create_ticket, TICKET),
         _harnessed("create_ticket", TICKET, estimated_tokens=6000)),
    ]


if __name__ == "__main__":
    for scenario, direct, harnessed in compare():
        print(f"{scenario}\n  direct:    {direct}\n  harnessed: {harnessed}")
