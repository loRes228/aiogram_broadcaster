from asyncio import create_task
from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Set

from aiogram.dispatcher.event.handler import CallableObject, CallbackType


if TYPE_CHECKING:
    from asyncio import Task


class Callback(NamedTuple):
    callback: CallableObject
    as_task: bool
    kwargs: Dict[str, Any]


class EventObserver:
    kwargs: Dict[str, Any]
    callbacks: List[Callback]
    tasks: Set["Task[Any]"]

    __slots__ = (
        "callbacks",
        "kwargs",
        "tasks",
    )

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.callbacks = []
        self.tasks = set()

    def register(
        self,
        callback: CallbackType,
        *,
        as_task: bool = False,
        **kwargs: Any,
    ) -> None:
        self.callbacks.append(
            Callback(
                callback=CallableObject(callback=callback),
                as_task=as_task,
                kwargs=kwargs,
            ),
        )

    async def trigger(
        self,
        *,
        as_task: bool = False,
        **kwargs: Any,
    ) -> None:
        if not self.callbacks:
            return
        for callback in self.callbacks:
            data = {**callback.kwargs, **self.kwargs, **kwargs}
            if callback.as_task or as_task:
                task = create_task(callback.callback.call(**data))
                self.tasks.add(task)
                task.add_done_callback(self.tasks.discard)
            else:
                await callback.callback.call(**data)


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
        for trigger in self.__slots__:
            setattr(self, trigger, EventObserver(**kwargs))
