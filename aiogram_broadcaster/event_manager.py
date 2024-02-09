from contextlib import suppress
from typing import Any, Dict, List, NamedTuple

from aiogram.dispatcher.event.bases import CancelHandler, SkipHandler
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


class CallbackObject(NamedTuple):
    callable: CallableObject
    data: Dict[str, Any]


class EventObserver:
    callbacks: List[CallbackObject]

    __slots__ = ("callbacks",)

    def __init__(self) -> None:
        self.callbacks = []

    def register(self, callback: CallbackType, **data: Any) -> None:
        self.callbacks.append(
            CallbackObject(
                callable=CallableObject(callback=callback),
                data=data,
            ),
        )

    async def trigger(self, **data: Any) -> None:
        if not self.callbacks:
            return
        with suppress(SkipHandler, CancelHandler):
            for callback in self.callbacks:
                await callback.callable.call(**callback.data, **data)


class EventManager:
    startup: EventObserver
    shutdown: EventObserver
    complete: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver

    __slots__ = (
        "complete",
        "failed_sent",
        "shutdown",
        "startup",
        "success_sent",
    )

    def __init__(self) -> None:
        for event in self.__slots__:
            setattr(self, event, EventObserver())
