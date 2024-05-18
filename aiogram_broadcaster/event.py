from typing import Any, Callable, Dict, Iterator, List, Optional

from aiogram.dispatcher.event.handler import CallableObject, CallbackType

from .utils.chain import ChainObject
from .utils.interrupt import suppress_interrupt


class EventObserver:
    callbacks: List[CallableObject]

    def __init__(self) -> None:
        self.callbacks = []

    def __iter__(self) -> Iterator[CallbackType]:
        return iter(callback.callback for callback in self.callbacks)

    def __len__(self) -> int:
        return len(self.callbacks)

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


class EventRouter(ChainObject["EventRouter"], sub_name="event"):
    started: EventObserver
    stopped: EventObserver
    completed: EventObserver
    before_sent: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver
    observers: Dict[str, EventObserver]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.started = EventObserver()
        self.stopped = EventObserver()
        self.completed = EventObserver()
        self.before_sent = EventObserver()
        self.success_sent = EventObserver()
        self.failed_sent = EventObserver()
        self.observers = {
            "started": self.started,
            "stopped": self.stopped,
            "completed": self.completed,
            "before_sent": self.before_sent,
            "success_sent": self.success_sent,
            "failed_sent": self.failed_sent,
        }

    def __getitem__(self, item: str) -> EventObserver:
        return self.observers[item]


class EventManager(EventRouter):
    __chain_root__ = True

    async def emit_event(self, __event_name: str, /, **context: Any) -> Dict[str, Any]:
        collected_data: Dict[str, Any] = {}
        with suppress_interrupt():
            for event in self.chain_tail:
                for callback in event.observers[__event_name].callbacks:
                    result = await callback.call(**context, **collected_data)
                    if result and isinstance(result, dict):
                        collected_data.update(result)
        return collected_data

    async def emit_started(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("started", **context)

    async def emit_stopped(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("stopped", **context)

    async def emit_completed(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("completed", **context)

    async def emit_before_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("before_sent", **context)

    async def emit_success_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("success_sent", **context)

    async def emit_failed_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("failed_sent", **context)
