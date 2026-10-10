"""Harnessed LLM call: the model is a tool, so policy, budget and telemetry apply."""
import sys

from _setup import show
from dotenv import load_dotenv

from agent_platform import AgentHarness, AgentRegistry, RunRequest, load_manifest
from agent_platform.llm import make_llm
from agent_platform.policy import PolicyEngine
from agent_platform.telemetry import InMemoryTelemetry
from agent_platform.tools import ToolRegistry, ToolResult

SYSTEM = "Classify the support request as one of: outage, billing, how-to. Reply with the label."


def classify(llm, text: str) -> ToolResult:
    completion = llm.complete(SYSTEM, text)
    return ToolResult(completion.text, completion.tokens)


def build_llm_harness(llm) -> tuple[AgentHarness, InMemoryTelemetry]:
    registry = AgentRegistry()
    registry.register(load_manifest("manifests/triage-agent.yaml"))
    tools = ToolRegistry()
    tools.add("classify_ticket", lambda text: classify(llm, text))
    telemetry = InMemoryTelemetry()
    return AgentHarness(registry, tools, PolicyEngine(), telemetry), telemetry


if __name__ == "__main__":
    load_dotenv()
    harness, telemetry = build_llm_harness(make_llm())
    text = " ".join(sys.argv[1:]) or "The checkout page has been down for an hour"
    result = harness.run(RunRequest("triage-agent", "Classify request", "classify_ticket",
                                    {"text": text}, estimated_tokens=800))
    show(result, telemetry)
