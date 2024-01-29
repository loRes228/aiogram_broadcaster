from asyncio import create_task
from typing import TYPE_CHECKING, Any, List, Set

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


if TYPE_CHECKING:
    from asyncio import Task

    from .mailer import Mailer


class TriggerObserver:
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

    def trigger(self, mailer: "Mailer", **kwargs: Any) -> None:
        if not self.callbacks:
            return
        kwargs.update(
            mailer=mailer,
            bot=self.bot,
            **self.dispatcher.workflow_data,
        )
        for callback in self.callbacks:
            task = create_task(callback.call(**kwargs))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)


class TriggerManager:
    startup: TriggerObserver
    shutdown: TriggerObserver
    complete: TriggerObserver
    success_sent: TriggerObserver
    failed_sent: TriggerObserver

    __slots__ = (
        "startup",
        "shutdown",
        "complete",
        "success_sent",
        "failed_sent",
    )

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        for trigger in self.__slots__:
            setattr(self, trigger, TriggerObserver(bot=bot, dispatcher=dispatcher))
