from contextlib import suppress
from typing import Any, Callable, Dict, List, NoReturn, Optional

from aiogram.dispatcher.event.bases import CancelHandler, SkipHandler
from aiogram.dispatcher.event.handler import CallableObject, CallbackType

from .utils.chain import ChainObject


class SkipEvent(Exception):  # noqa: N818
    pass


def skip_event() -> NoReturn:
    raise SkipEvent


class EventObserver:
    callbacks: List[CallableObject]

    def __init__(self) -> None:
        self.callbacks = []

    def __call__(self) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback)
            return callback

        return wrapper

    def register(self, *callbacks: CallbackType) -> "EventObserver":
        if not callbacks:
            raise ValueError("At least one callback must be provided to register.")
        for callback in callbacks:
            if not callable(callback):
                raise TypeError("The callback must be callable.")
            self.callbacks.append(CallableObject(callback=callback))
        return self


class Event(ChainObject["Event"], sub_name="event"):
    started: EventObserver
    stopped: EventObserver
    completed: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver
    observers: Dict[str, EventObserver]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

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


class EventManager(Event):
    __chain_root__ = True

    async def emit_event(self, __event_name: str, /, **kwargs: Any) -> Dict[str, Any]:
        merged_kwargs: Dict[str, Any] = {}
        with suppress(SkipEvent, SkipHandler, CancelHandler):
            for event in self.chain_tail:
                for callback in event.observers[__event_name].callbacks:
                    result = await callback.call(**kwargs, **merged_kwargs)
                    if result and isinstance(result, dict):
                        merged_kwargs.update(result)
        return merged_kwargs

    async def emit_started(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.emit_event("started", **kwargs)

    async def emit_stopped(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.emit_event("stopped", **kwargs)

    async def emit_completed(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.emit_event("completed", **kwargs)

    async def emit_success_sent(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.emit_event("success_sent", **kwargs)

    async def emit_failed_sent(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.emit_event("failed_sent", **kwargs)
