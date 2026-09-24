"""A synchronous, in-process event bus (ADR-0002).

Deliberately tiny: the point is the *shape* — contexts publish facts and
subscribe to facts, never call each other. In production the same publish
would write to a transactional outbox and a relay would feed a broker.
"""

from collections import defaultdict
from collections.abc import Callable
from typing import Any

Handler = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
