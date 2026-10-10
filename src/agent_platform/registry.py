from .manifest import AgentManifest


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> None:
        if manifest.agent_id in self._agents:
            raise ValueError(f"agent already registered: {manifest.agent_id}")
        self._agents[manifest.agent_id] = manifest

    def get(self, agent_id: str) -> AgentManifest:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent: {agent_id}") from exc

    def by_owner(self, owner: str) -> list[AgentManifest]:
        return [a for a in self._agents.values() if a.owner == owner]
