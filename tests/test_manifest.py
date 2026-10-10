import pytest
from pydantic import ValidationError

from agent_platform.manifest import AgentManifest


def test_owner_is_required():
    with pytest.raises(ValidationError):
        AgentManifest(agent_id="a-1", owner="", purpose="Valid purpose")

def test_high_risk_agent_requires_human_approval():
    with pytest.raises(ValidationError):
        AgentManifest(agent_id="pay-agent", owner="payments", purpose="Issue payments",
                      risk_tier="high", allowed_tools=["pay"])


def test_invalid_risk_tier_is_rejected():
    with pytest.raises(ValidationError):
        AgentManifest(agent_id="a-1", owner="team-a", purpose="Valid purpose", risk_tier="x")


def test_support_manifest_loads():
    from agent_platform import load_manifest
    assert load_manifest("manifests/support-agent.yaml").allowed_tools == ["create_ticket"]
