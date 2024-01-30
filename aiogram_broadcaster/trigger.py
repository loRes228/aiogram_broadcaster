from asyncio import create_task
from typing import TYPE_CHECKING, Any, List, NamedTuple, Set

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


if TYPE_CHECKING:
    from asyncio import Task

    from .mailer import Mailer


class Callback(NamedTuple):
    callback: CallableObject
    as_task: bool


class TriggerObserver:
    bot: Bot
    dispatcher: Dispatcher
    callbacks: List[Callback]
    tasks: Set["Task[Any]"]

    __slots__ = (
        "bot",
        "callbacks",
        "dispatcher",
        "tasks",
    )

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.callbacks = []
        self.tasks = set()

    def register(self, callback: CallbackType, *, as_task: bool = False) -> None:
        self.callbacks.append(
            Callback(
                callback=CallableObject(callback=callback),
                as_task=as_task,
            ),
        )

    async def trigger(self, mailer: "Mailer", *, as_task: bool = False, **kwargs: Any) -> None:
        if not self.callbacks:
            return
        kwargs.update(
            mailer=mailer,
            bot=self.bot,
            **self.dispatcher.workflow_data,
        )
        for callback in self.callbacks:
            if callback.as_task or as_task:
                task = create_task(callback.callback.call(**kwargs))
                self.tasks.add(task)
                task.add_done_callback(self.tasks.discard)
            else:
                await callback.callback.call(**kwargs)


class TriggerManager:
    startup: TriggerObserver
    shutdown: TriggerObserver
    complete: TriggerObserver
    success_sent: TriggerObserver
    failed_sent: TriggerObserver

    __slots__ = (
        "complete",
        "failed_sent",
        "shutdown",
        "startup",
        "success_sent",
    )

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        for trigger in self.__slots__:
            setattr(self, trigger, TriggerObserver(bot=bot, dispatcher=dispatcher))
