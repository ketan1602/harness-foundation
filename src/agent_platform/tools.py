from collections.abc import Callable


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
