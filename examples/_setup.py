"""Shared wiring for the demo and experiments."""
from pathlib import Path

from agent_platform import AgentHarness, AgentRegistry, load_manifest
from agent_platform.policy import PolicyEngine
from agent_platform.telemetry import InMemoryTelemetry
from agent_platform.tools import ToolRegistry

MANIFEST = Path(__file__).resolve().parent.parent / "manifests" / "support-agent.yaml"


def create_ticket(subject: str, priority: str) -> dict:
    return {"ticket_id": "T-1001", "subject": subject, "priority": priority}


def delete_customer(customer_id: str) -> dict:
    return {"deleted": customer_id}


def build_harness() -> tuple[AgentHarness, InMemoryTelemetry]:
    registry = AgentRegistry()
    registry.register(load_manifest(MANIFEST))
    tools = ToolRegistry()
    tools.add("create_ticket", create_ticket)
    tools.add("delete_customer", delete_customer)
    telemetry = InMemoryTelemetry()
    return AgentHarness(registry, tools, PolicyEngine(), telemetry), telemetry


def show(result, telemetry) -> None:
    """Demo output; examples are CLI scripts, so stdout is the interface."""
    print(f"status={result.status} reason={result.reason} steps={result.usage.steps}")
    print("output:", result.output)
    for event in telemetry.events:
        print(" ", event.name, {k: v for k, v in event.attributes.items() if k != "span_id"})
