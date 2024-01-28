from asyncio import create_task
from typing import TYPE_CHECKING, Any, List, Set

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


if TYPE_CHECKING:
    from asyncio import Task


class EventObserver:
    bot: Bot
    dispatcher: Dispatcher
    callbacks: List[CallableObject]
    tasks: Set["Task[Any]"]

    __slots__ = (
        "bot",
        "dispatcher",
        "callbacks",
        "tasks",
    )

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.callbacks = []
        self.tasks = set()

    def register(self, callback: CallbackType) -> None:
        self.callbacks.append(CallableObject(callback=callback))

    def trigger(self, **kwargs: Any) -> None:
        if not self.callbacks:
            return
        kwargs.update(bot=self.bot, **self.dispatcher.workflow_data)
        for callback in self.callbacks:
            task = create_task(callback.call(**kwargs))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)


class EventManager:
    startup: EventObserver
    shutdown: EventObserver
    complete: EventObserver
    success_sent: EventObserver
    failed_sent: EventObserver

    __slots__ = (
        "startup",
        "shutdown",
        "complete",
        "success_sent",
        "failed_sent",
    )

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        for event in self.__slots__:
            setattr(self, event, EventObserver(bot=bot, dispatcher=dispatcher))
