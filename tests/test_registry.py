import pytest

from agent_platform.manifest import AgentManifest
from agent_platform.registry import AgentRegistry


def test_duplicate_agent_is_rejected():
    registry = AgentRegistry()
    manifest = AgentManifest(agent_id="agent-1", owner="team-a", purpose="Test tasks")
    registry.register(manifest)
    with pytest.raises(ValueError):
        registry.register(manifest)


def test_by_owner_filters():
    registry = AgentRegistry()
    registry.register(AgentManifest(agent_id="agent-1", owner="team-a", purpose="Test tasks"))
    registry.register(AgentManifest(agent_id="agent-2", owner="team-b", purpose="Test tasks"))
    assert [m.agent_id for m in registry.by_owner("team-a")] == ["agent-1"]
