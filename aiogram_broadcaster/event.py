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
            self.callbacks.append(CallableObject(callback=callback))
        return self

    async def trigger(self, **kwargs: Any) -> None:
        with suppress(SkipEvent, SkipHandler, CancelHandler):
            merged_kwargs: Dict[str, Any] = {}
            for callback in self.callbacks:
                result = await callback.call(
                    **kwargs,
                    **merged_kwargs,
                )
                if result and isinstance(result, dict):
                    merged_kwargs.update(result)


class EventRouter(ChainObject["EventRouter"], sub_name="event"):
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


class EventManager(EventRouter):
    __chain_root__ = True

    async def emit_started(self, **kwargs: Any) -> None:
        for event in self.chain_tail:
            await event.started.trigger(**kwargs)

    async def emit_stopped(self, **kwargs: Any) -> None:
        for event in self.chain_tail:
            await event.stopped.trigger(**kwargs)

    async def emit_completed(self, **kwargs: Any) -> None:
        for event in self.chain_tail:
            await event.completed.trigger(**kwargs)

    async def emit_success_sent(self, **kwargs: Any) -> None:
        for event in self.chain_tail:
            await event.success_sent.trigger(**kwargs)

    async def emit_failed_sent(self, **kwargs: Any) -> None:
        for event in self.chain_tail:
            await event.failed_sent.trigger(**kwargs)
