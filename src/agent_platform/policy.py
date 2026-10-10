from dataclasses import dataclass

from .manifest import AgentManifest


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str

class PolicyEngine:
    def authorize_tool(self, manifest: AgentManifest, tool_name: str) -> PolicyDecision:
        if tool_name not in manifest.allowed_tools:
            return PolicyDecision(False, f"tool_not_allowed:{tool_name}")
        return PolicyDecision(True, "allowed")
