from dataclasses import dataclass, field
from uuid import uuid4

from .budget import BudgetController, BudgetExceeded, Usage
from .policy import PolicyEngine
from .registry import AgentRegistry
from .telemetry import InMemoryTelemetry
from .tools import ToolRegistry


@dataclass(frozen=True)
class RunRequest:
    agent_id: str
    task: str
    tool_name: str
    tool_args: dict
    estimated_tokens: int = 500
    estimated_cost_usd: float = 0.01
    trace_id: str = field(default_factory=lambda: uuid4().hex)


@dataclass(frozen=True)
class RunResult:
    status: str  # completed | blocked | terminated | failed
    output: object | None
    reason: str | None
    usage: Usage


class AgentHarness:
    """Mediates every tool call: authorize, budget, execute, record."""

    def __init__(self, registry: AgentRegistry, tools: ToolRegistry,
                 policy: PolicyEngine, telemetry: InMemoryTelemetry):
        self.registry = registry
        self.tools = tools
        self.policy = policy
        self.telemetry = telemetry

    def run(self, request: RunRequest) -> RunResult:
        manifest = self.registry.get(request.agent_id)
        budget = BudgetController(manifest.budget)
        emit = self._emitter(request)
        emit("agent.run.started", owner=manifest.owner, risk_tier=manifest.risk_tier)

        decision = self.policy.authorize_tool(manifest, request.tool_name)
        if not decision.allowed:
            emit("agent.run.blocked", reason=decision.reason)
            return RunResult("blocked", None, decision.reason, budget.usage)

        try:
            budget.consume(request.estimated_tokens, request.estimated_cost_usd)
            output = self.tools.call(request.tool_name, **request.tool_args)
        except BudgetExceeded as exc:
            emit("agent.run.terminated", reason=str(exc))
            return RunResult("terminated", None, str(exc), budget.usage)
        except Exception as exc:  # noqa: BLE001 - untrusted tool code: record and report
            emit("agent.run.failed", error_type=type(exc).__name__, error=str(exc))
            return RunResult("failed", None, str(exc), budget.usage)

        emit("agent.run.completed", tool=request.tool_name, cost_usd=budget.usage.cost_usd)
        return RunResult("completed", output, None, budget.usage)

    def _emitter(self, request: RunRequest):
        def emit(name: str, **attributes):
            self.telemetry.emit(name, trace_id=request.trace_id,
                                agent_id=request.agent_id, **attributes)
        return emit
