from asyncio import Event, wait_for
from asyncio.exceptions import TimeoutError
from contextlib import suppress
from logging import Logger
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import AiogramError

from aiogram_broadcaster.models import BroadcastStatistic, MailerData
from aiogram_broadcaster.status import MailerStatus
from aiogram_broadcaster.storage import Storage


class Mailer:
    id: int
    bot: Bot
    storage: Storage
    data: MailerData
    logger: Logger
    status: MailerStatus
    stop_event: Event
    success: int
    failed: int

    __slots__ = (
        "id",
        "bot",
        "storage",
        "data",
        "logger",
        "status",
        "stop_event",
        "success",
        "failed",
    )

    def __init__(
        self,
        *,
        id_: Optional[int] = None,
        bot: Bot,
        storage: Storage,
        data: MailerData,
        logger: Logger,
    ) -> None:
        self.id = id_ or id(self)
        self.bot = bot
        self.storage = storage
        self.data = data.model_copy()
        self.logger = logger
        self.status = MailerStatus.STOPPED
        self.stop_event = Event()
        self.success = 0
        self.failed = 0

    async def run(self) -> None:
        if self.status == MailerStatus.COMPLETED or len(self.data.chat_ids) == 0:
            raise RuntimeError("No chats for broadcasting.")

        self.logger.info("Start broadcaster id=%d", self.id)
        self.status = MailerStatus.STARTED
        self.stop_event.clear()

        for chat_id in self.data.chat_ids[:]:
            if self.stop_event.is_set():
                break
            await self.send(chat_id=chat_id)
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self.pop_chat()
            if not is_last_chat:
                await self.sleep()
        else:
            self.status = MailerStatus.COMPLETED

    def stop(self) -> bool:
        if self.status is MailerStatus.COMPLETED:
            return False
        self.logger.info("Stop broadcaster id=%d", self.id)
        self.stop_event.set()
        self.status = MailerStatus.STOPPED
        return True

    async def sleep(self) -> None:
        with suppress(TimeoutError):
            await wait_for(
                fut=self.stop_event.wait(),
                timeout=self.data.settings.interval,
            )

    async def send(self, *, chat_id: int) -> None:
        try:
            await self.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=self.data.settings.from_chat_id,
                message_id=self.data.settings.message_id,
                disable_notification=not self.data.settings.notifications,
                protect_content=self.data.settings.protect_content,
            )
        except AiogramError as error:
            self.failed += 1
            self.logger.info(
                "Failed to send message to chat id=%d, error: %s",
                chat_id,
                type(error).__name__,
            )
        else:
            self.success += 1
            self.logger.info("Success send message to chat id=%d", chat_id)

    async def pop_chat(self) -> None:
        await self.storage.pop_chat(mailer_id=self.id)
        self.data.chat_ids.pop(0)

    def statistic(self) -> BroadcastStatistic:
        return BroadcastStatistic(
            total_chats=self.data.settings.total_chats,
            success=self.success,
            failed=self.failed,
            ratio=(self.success / self.data.settings.total_chats) * 100,
        )
