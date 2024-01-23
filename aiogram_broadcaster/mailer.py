from asyncio import Event, TimeoutError, create_task, wait_for
from contextlib import suppress
from logging import Logger
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.handler import CallableObject
from aiogram.exceptions import AiogramError

from .models import MailerData, Statistic
from .storage import Storage


if TYPE_CHECKING:
    from asyncio import Task


class Mailer:
    data: MailerData
    bot: Bot
    dispatcher: Dispatcher
    storage: Storage
    logger: Logger
    mailers: Dict[int, "Mailer"]
    callback_on_failed: Optional[CallableObject]
    callback_tasks: "Set[Task[Any]]"
    _id: int
    stop_event: Event
    success: int
    failed: int

    __slots__ = (
        "data",
        "bot",
        "dispatcher",
        "storage",
        "logger",
        "mailers",
        "callback_on_failed",
        "callback_tasks",
        "_id",
        "stop_event",
        "success",
        "failed",
    )

    def __init__(
        self,
        *,
        data: MailerData,
        bot: Bot,
        dispatcher: Dispatcher,
        storage: Storage,
        logger: Logger,
        mailers: Dict[int, "Mailer"],
        callback_on_failed: Optional[CallableObject],
        callback_tasks: "Set[Task[Any]]",
        id_: Optional[int] = None,
    ) -> None:
        self.data = data
        self.bot = bot
        self.dispatcher = dispatcher
        self.storage = storage
        self.logger = logger
        self.mailers = mailers
        self.callback_on_failed = callback_on_failed
        self.callback_tasks = callback_tasks
        self._id = id_ or id(self)
        self.stop_event = Event()
        self.success = 0
        self.failed = 0
        self.mailers[self._id] = self
        self.stop_event.set()

    @property
    def id(self) -> int:
        return self._id

    async def run(self) -> None:
        if self.is_working() or len(self.data.chat_ids) == 0:
            return
        self.logger.info("Run broadcaster id=%d.", self.id)
        self.stop_event.clear()
        for chat_id in self.data.chat_ids[:]:
            if self.stop_event.is_set():
                break
            await self._send(chat_id=chat_id)
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self._pop_chat()
            if not is_last_chat:
                await self._sleep()
        else:
            self.stop_event.set()
            await self.delete()

    def stop(self) -> bool:
        if not self.is_working():
            return False
        self.logger.info("Stop broadcaster id=%d.", self.id)
        self.stop_event.set()
        return True

    async def delete(self) -> None:
        self.logger.info("Delete broadcaster id=%d.", self.id)
        self.stop()
        del self.mailers[self.id]
        await self.storage.delete_data(mailer_id=self.id)

    def is_working(self) -> bool:
        return not self.stop_event.is_set()

    def statistic(self) -> Statistic:
        return Statistic(
            total_chats=self.data.settings.total_chats,
            success=self.success,
            failed=self.failed,
            ratio=(self.success / self.data.settings.total_chats) * 100,
        )

    async def _send(self, chat_id: int) -> None:
        try:
            await self.data.settings.message.as_(self.bot).send_copy(
                chat_id=chat_id,
                disable_notification=self.data.settings.disable_notification,
            )
        except AiogramError as error:
            self.failed += 1
            self.logger.info(
                "Failed to send message to chat id=%d, error: %s.",
                chat_id,
                type(error).__name__,
            )
            if self.callback_on_failed:
                task = create_task(
                    self.callback_on_failed.call(
                        error=error,
                        chat_id=chat_id,
                        mailer_id=self.id,
                        bot=self.bot,
                        dispatcher=self.dispatcher,
                        **self.dispatcher.workflow_data,
                    ),
                )
                self.callback_tasks.add(task)
                task.add_done_callback(self.callback_tasks.discard)
        else:
            self.success += 1
            self.logger.info(
                "Successfully sent a message to chat id=%d.",
                chat_id,
            )

    async def _sleep(self) -> None:
        with suppress(TimeoutError):
            await wait_for(
                fut=self.stop_event.wait(),
                timeout=self.data.settings.interval,
            )

    async def _pop_chat(self) -> None:
        self.data.chat_ids.pop(0)
        await self.storage.pop_chat(mailer_id=self.id)

    def __repr__(self) -> str:
        return f"Mailer(id={self.id}, is_working={self.is_working()})"

    def __str__(self) -> str:
        statistic = self.statistic()
        return ", ".join(
            f"{key}={value}"  # fmt: skip
            for key, value in statistic._asdict().items()
        )
