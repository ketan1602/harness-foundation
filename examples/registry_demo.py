"""A registry answers fleet questions: which agents exist, and who owns them."""
from _setup import MANIFEST

from agent_platform import AgentRegistry, load_manifest

TRIAGE = MANIFEST.with_name("triage-agent.yaml")


def build_registry() -> AgentRegistry:
    registry = AgentRegistry()
    for path in (MANIFEST, TRIAGE):
        registry.register(load_manifest(path))
    return registry


if __name__ == "__main__":
    registry = build_registry()
    for manifest in registry.by_owner("customer-platform"):
        print(manifest.agent_id, manifest.risk_tier, manifest.allowed_tools, manifest.budget)
    try:
        registry.register(load_manifest(MANIFEST))
    except ValueError as exc:
        print("duplicate rejected:", exc)
