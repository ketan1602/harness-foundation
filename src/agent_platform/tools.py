from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    """Optional tool return type carrying measured usage (cost None = keep the estimate)."""
    output: object
    tokens: int
    cost_usd: float | None = None


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., object]] = {}

    def add(self, name: str, fn: Callable[..., object]) -> None:
        if name in self._tools:
            raise ValueError(f"duplicate tool: {name}")
        self._tools[name] = fn

    def call(self, name: str, **kwargs):
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name](**kwargs)
