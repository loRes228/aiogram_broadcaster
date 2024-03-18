from contextlib import suppress
from typing import Any, Callable, Dict, Generator, List, NoReturn, Optional, Tuple

from aiogram.dispatcher.event.handler import CallableObject, CallbackType


class SkipEvent(Exception):  # noqa: N818
    pass


def skip_event() -> NoReturn:
    raise SkipEvent


class EventObserver:
    callbacks: List[Tuple[CallableObject, Dict[str, Any]]]

    def __init__(self) -> None:
        self.callbacks = []

    def __call__(self) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback=callback)
            return callback

        return wrapper

    def register(self, callback: CallbackType, **kwargs: Any) -> None:
        self.callbacks.append((CallableObject(callback=callback), kwargs))

    async def trigger(self, **kwargs: Any) -> None:
        with suppress(SkipEvent):
            for callback, callback_kwargs in self.callbacks:
                await callback.call(**kwargs, **callback_kwargs)


class EventRouter:
    name: str
    started: EventObserver
    stopped: EventObserver
    completed: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver
    observers: Dict[str, EventObserver]
    sub_events: List["EventRouter"]
    _parent_event: Optional["EventRouter"]

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or hex(id(self))

        self.started = EventObserver()
        self.stopped = EventObserver()
        self.completed = EventObserver()
        self.success_sent = EventObserver()
        self.failed_sent = EventObserver()

        self.observers = {
            "started": self.started,
            "stopped": self.stopped,
            "completed": self.completed,
            "success_sent": self.success_sent,
            "failed_sent": self.failed_sent,
        }

        self.sub_events = []
        self._parent_event = None

    def __repr__(self) -> str:
        return f"EventRouter(name={self.name!r})"

    def __str__(self) -> str:
        return self.name

    @property
    def chain_events(self) -> Generator["EventRouter", None, None]:
        yield self
        for sub_event in self.sub_events:
            yield from sub_event.chain_events

    @property
    def parent_event(self) -> Optional["EventRouter"]:
        return self._parent_event

    @parent_event.setter
    def parent_event(self, event: "EventRouter") -> None:
        if not isinstance(event, EventRouter):
            raise TypeError(
                f"Event must be an instance of EventRouter, not a {type(event).__name__}.",
            )
        if self._parent_event:
            raise RuntimeError(f"The event is already attached to {self._parent_event!r}.")
        if self == event:
            raise RuntimeError("Cannot include event on itself.")

        parent: Optional[EventRouter] = event
        while parent:
            if self == parent:
                raise RuntimeError("Circular referencing detected.")
            parent = parent.parent_event

        self._parent_event = event
        event.sub_events.append(self)

    def include_event(self, event: "EventRouter") -> "EventRouter":
        if not isinstance(event, EventRouter):
            raise TypeError(
                f"Event must be an instance of EventRouter, not a {type(event).__name__}.",
            )
        event.parent_event = self
        return event

    def include_events(self, *events: "EventRouter") -> None:
        if not events:
            raise ValueError("At least one event must be provided to include.")
        for event in events:
            self.include_event(event=event)

    async def emit_started(self, **kwargs: Any) -> None:
        kwargs.update(event_router=self)
        for event in self.chain_events:
            await event.started.trigger(**kwargs)

    async def emit_stopped(self, **kwargs: Any) -> None:
        kwargs.update(event_router=self)
        for event in self.chain_events:
            await event.stopped.trigger(**kwargs)

    async def emit_completed(self, **kwargs: Any) -> None:
        kwargs.update(event_router=self)
        for event in self.chain_events:
            await event.completed.trigger(**kwargs)

    async def emit_success_sent(self, **kwargs: Any) -> None:
        kwargs.update(event_router=self)
        for event in self.chain_events:
            await event.success_sent.trigger(**kwargs)

    async def emit_failed_sent(self, **kwargs: Any) -> None:
        kwargs.update(event_router=self)
        for event in self.chain_events:
            await event.failed_sent.trigger(**kwargs)


class RootEventRouter(EventRouter):
    @property
    def parent_event(self) -> Optional[EventRouter]:
        return None

    @parent_event.setter
    def parent_event(self, event: EventRouter) -> None:  # noqa: ARG002
        raise RuntimeError("RootEventRouter cannot be attached to another event.")
