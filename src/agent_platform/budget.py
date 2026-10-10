from dataclasses import dataclass

from .manifest import BudgetSpec


@dataclass
class Usage:
    steps: int = 0
    tokens: int = 0
    cost_usd: float = 0.0

class BudgetExceeded(RuntimeError):
    pass

class BudgetController:
    def __init__(self, spec: BudgetSpec):
        self.spec = spec
        self.usage = Usage()

    def consume(self, tokens: int, cost_usd: float) -> None:
        self.usage.steps += 1
        self.usage.tokens += tokens
        self.usage.cost_usd += cost_usd
        if self.usage.steps > self.spec.max_steps:
            raise BudgetExceeded("maximum steps exceeded")
        if self.usage.tokens > self.spec.max_tokens:
            raise BudgetExceeded("maximum tokens exceeded")
        if self.usage.cost_usd > self.spec.max_cost_usd:
            raise BudgetExceeded("maximum cost exceeded")
