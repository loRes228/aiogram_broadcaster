from asyncio import Event, TimeoutError, wait_for
from contextlib import suppress
from logging import Logger
from typing import Dict, Optional

from aiogram import Bot
from aiogram.exceptions import AiogramError

from .models import BroadcastStatistic, MailerData
from .storage import Storage


class Mailer:
    data: MailerData
    bot: Bot
    storage: Storage
    logger: Logger
    _mailers: Dict[int, "Mailer"]
    _id: int
    stop_event: Event
    _success: int
    _failed: int

    __slots__ = (
        "data",
        "bot",
        "storage",
        "logger",
        "_mailers",
        "_id",
        "stop_event",
        "_success",
        "_failed",
    )

    def __init__(
        self,
        data: MailerData,
        bot: Bot,
        storage: Storage,
        logger: Logger,
        mailers: Dict[int, "Mailer"],
        id_: Optional[int] = None,
    ) -> None:
        self.data = data
        self.bot = bot
        self.storage = storage
        self.logger = logger
        self._mailers = mailers
        self._id = id_ or id(self)
        self.stop_event = Event()
        self._success = 0
        self._failed = 0
        self._mailers[self._id] = self
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
        del self._mailers[self.id]
        await self.storage.delete_data(mailer_id=self.id)

    def is_working(self) -> bool:
        return not self.stop_event.is_set()

    def statistic(self) -> BroadcastStatistic:
        return BroadcastStatistic(
            total_chats=self.data.settings.total_chats,
            success=self._success,
            failed=self._failed,
            ratio=(self._success / self.data.settings.total_chats) * 100,
        )

    async def _send(self, chat_id: int) -> None:
        try:
            await self.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=self.data.settings.from_chat_id,
                message_id=self.data.settings.message_id,
                disable_notification=not self.data.settings.notifications,
                protect_content=self.data.settings.protect_content,
            )
        except AiogramError as error:
            self.logger.info(
                "Failed to send message to chat id=%d, error: %s.",
                chat_id,
                type(error).__name__,
            )
            self._failed += 1
        else:
            self.logger.info(
                "Successfully sent a message to chat id=%d.",
                chat_id,
            )
            self._success += 1

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
