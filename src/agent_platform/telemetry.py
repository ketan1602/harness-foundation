from collections import Counter
from dataclasses import dataclass, field
from time import time
from uuid import uuid4


@dataclass(frozen=True)
class Event:
    name: str
    attributes: dict
    timestamp: float = field(default_factory=time)


class InMemoryTelemetry:
    """Collects events; every event carries trace_id and span_id."""

    def __init__(self):
        self.events: list[Event] = []

    def emit(self, name: str, *, trace_id: str, **attributes) -> None:
        attributes |= {"trace_id": trace_id, "span_id": uuid4().hex[:16]}
        self.events.append(Event(name=name, attributes=attributes))

    def counts(self) -> Counter:
        return Counter(e.name for e in self.events)
