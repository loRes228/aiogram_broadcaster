from contextlib import suppress
from typing import Any, Dict, List, NamedTuple

from aiogram.dispatcher.event.bases import CancelHandler, SkipHandler
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


class Callback(NamedTuple):
    callback: CallableObject
    kwargs: Dict[str, Any]

    async def call(self, **kwargs: Any) -> None:
        await self.callback.call(**self.kwargs, **kwargs)


class EventObserver:
    kwargs: Dict[str, Any]
    callbacks: List[Callback]

    __slots__ = (
        "callbacks",
        "kwargs",
    )

    def __init__(self, kwargs: Dict[str, Any]) -> None:
        self.kwargs = kwargs
        self.callbacks = []

    def register(self, callback: CallbackType, **kwargs: Any) -> None:
        self.callbacks.append(
            Callback(
                callback=CallableObject(callback=callback),
                kwargs=kwargs,
            ),
        )

    async def trigger(self, **kwargs: Any) -> None:
        if not self.callbacks:
            return
        with suppress(SkipHandler, CancelHandler):
            for callback in self.callbacks:
                await callback.call(**self.kwargs, **kwargs)


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

    def __init__(self, **kwargs: Any) -> None:
        for event in self.__slots__:
            setattr(self, event, EventObserver(kwargs=kwargs))
