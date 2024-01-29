from asyncio import Event, TimeoutError, wait_for
from contextlib import suppress
from logging import Logger
from typing import Dict, Optional

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from .models import MailerData, Statistic
from .storage import MailerStorage
from .trigger import TriggerManager


class Mailer:
    bot: Bot
    dispatcher: Dispatcher
    logger: Logger
    data: MailerData
    storage: MailerStorage
    trigger_manager: TriggerManager
    _mailers: Dict[int, "Mailer"]
    _id: int
    _success_sent: int
    _failed_sent: int
    _delay: float
    _stop_event: Event

    __slots__ = (
        "bot",
        "dispatcher",
        "logger",
        "data",
        "storage",
        "trigger_manager",
        "_mailers",
        "_id",
        "_success_sent",
        "_failed_sent",
        "_delay",
        "_stop_event",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        logger: Logger,
        data: MailerData,
        storage: MailerStorage,
        trigger_manager: TriggerManager,
        mailers: Dict[int, "Mailer"],
        id_: Optional[int] = None,
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.logger = logger
        self.data = data
        self.storage = storage
        self.trigger_manager = trigger_manager
        self._mailers = mailers
        self._id = id_ or id(self)
        self._success_sent = 0
        self._failed_sent = 0
        self._delay = self.data.settings.interval / self.data.settings.total_chats
        self._stop_event = Event()
        self._mailers[self._id] = self
        self._stop_event.set()

    def __repr__(self) -> str:
        return "Mailer(id=%d, total_chats=%d, is_working=%s)" % (
            self.id,
            len(self.data.chat_ids),
            self.is_working(),
        )

    def __str__(self) -> str:
        return ", ".join(
            f"{key}={value}"  # fmt: skip
            for key, value in self.statistic()._asdict().items()
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def message(self) -> Message:
        return self.data.settings.message.as_(bot=self.bot)

    @property
    def interval(self) -> float:
        return self.data.settings.interval

    def is_working(self) -> bool:
        return not self._stop_event.is_set()

    def statistic(self) -> Statistic:
        return Statistic(
            total_chats=self.data.settings.total_chats,
            success=self._success_sent,
            failed=self._failed_sent,
            ratio=(self._success_sent / self.data.settings.total_chats) * 100,
        )

    async def delete(self) -> None:
        self.logger.info("Delete broadcaster id=%d", self.id)
        await self.stop()
        await self.storage.delete_data(mailer_id=self.id)
        del self._mailers[self.id]

    async def stop(self) -> None:
        if not self.is_working():
            return
        await self.trigger_manager.shutdown.trigger(mailer=self)
        self._stop_event.set()
        self.logger.info("Stop broadcaster id=%d", self.id)

    async def run(self) -> None:
        if self.is_working():
            raise RuntimeError(f"Mailer id={self.id} already started.")
        if not self.data.chat_ids:
            raise RuntimeError(f"Mailer id={self.id} has no chats.")

        await self.trigger_manager.startup.trigger(mailer=self)
        self._stop_event.clear()
        self.logger.info("Run broadcaster id=%d", self.id)

        for chat_id in self.data.chat_ids[:]:
            if self._stop_event.is_set():
                break
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self._send(chat_id=chat_id)
            await self._pop_chat()
            if not is_last_chat:
                await self._sleep()
        else:
            await self.trigger_manager.complete.trigger(mailer=self)
            await self.delete()
            self.logger.info("Broadcasting id=%d complete!", self.id)

    async def _send(self, chat_id: int) -> None:
        try:
            await self.message.send_copy(
                chat_id=chat_id,
                disable_notification=self.data.settings.disable_notification,
                reply_markup=self.data.settings.reply_markup,
            )
        except TelegramAPIError as error:
            self._failed_sent += 1
            await self.trigger_manager.failed_sent.trigger(
                mailer=self,
                as_task=True,
                error=error,
                chat_id=chat_id,
            )
            self.logger.info(
                "Failed to send message to chat id=%d, error: %s.",
                chat_id,
                type(error).__name__,
            )
        else:
            self._success_sent += 1
            await self.trigger_manager.success_sent.trigger(
                mailer=self,
                as_task=True,
                chat_id=chat_id,
            )
            self.logger.info(
                "Successfully sent a message to chat id=%d.",
                chat_id,
            )

    async def _pop_chat(self) -> None:
        await self.storage.pop_chat(mailer_id=self.id)
        self.data.chat_ids.pop(0)

    async def _sleep(self) -> None:
        with suppress(TimeoutError):
            await wait_for(
                fut=self._stop_event.wait(),
                timeout=self._delay,
            )
