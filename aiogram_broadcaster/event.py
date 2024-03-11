from contextlib import suppress
from typing import Any, Callable, Dict, List, NoReturn, Tuple

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
        if not self.callbacks:
            return
        with suppress(SkipEvent):
            for callback, callback_kwargs in self.callbacks:
                await callback.call(**kwargs, **callback_kwargs)


class EventRouter:
    started: EventObserver
    stopped: EventObserver
    completed: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver
    observers: Dict[str, EventObserver]

    def __init__(self) -> None:
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

    def include_event(self, event: "EventRouter") -> None:
        for event_name, observer in event.observers.items():
            self.observers[event_name].callbacks.extend(observer.callbacks)
