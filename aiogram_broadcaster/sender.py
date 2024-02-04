from asyncio import Event, TimeoutError, wait_for
from contextlib import suppress
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from .data import Data
from .event_manager import EventManager
from .storage.base import BaseMailerStorage


if TYPE_CHECKING:
    from .mailer import Mailer


class Sender:
    bot: Bot
    mailer: "Mailer"
    data: Data
    storage: BaseMailerStorage
    event: EventManager
    stop_event: Event
    success_sent: int
    failed_sent: int

    __slots__ = (
        "bot",
        "data",
        "event",
        "failed_sent",
        "mailer",
        "stop_event",
        "storage",
        "success_sent",
    )

    def __init__(
        self,
        bot: Bot,
        mailer: "Mailer",
        data: Data,
        storage: BaseMailerStorage,
        event: EventManager,
    ) -> None:
        self.bot = bot
        self.mailer = mailer
        self.data = data
        self.storage = storage
        self.event = event

        self.stop_event = Event()
        self.success_sent = 0
        self.failed_sent = 0

        self.stop_event.set()

    @property
    def message(self) -> Message:
        return self.data.settings.message.as_(bot=self.bot)

    async def start(self) -> bool:
        self.stop_event.clear()
        for chat_id in self.data.chat_ids[:]:
            if self.stop_event.is_set():
                break
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self.send(chat_id=chat_id)
            await self.pop_chat()
            if not is_last_chat:
                await self.sleep()
        else:
            return True
        return False

    def stop(self) -> None:
        self.stop_event.set()

    async def send(self, chat_id: int) -> None:
        try:
            await self.message.send_copy(
                chat_id=chat_id,
                disable_notification=self.data.settings.disable_notification,
                reply_markup=self.data.settings.reply_markup,
            )
        except TelegramAPIError as error:
            await self.handle_failed_sent(chat_id=chat_id, error=error)
        else:
            await self.handle_success_sent(chat_id=chat_id)

    async def handle_failed_sent(
        self,
        chat_id: int,
        error: TelegramAPIError,
    ) -> None:
        self.failed_sent += 1
        await self.event.failed_sent.trigger(
            mailer=self.mailer,
            as_task=True,
            error=error,
            chat_id=chat_id,
        )

    async def handle_success_sent(self, chat_id: int) -> None:
        self.success_sent += 1
        await self.event.success_sent.trigger(
            mailer=self.mailer,
            as_task=True,
            chat_id=chat_id,
        )

    async def pop_chat(self) -> None:
        self.data.chat_ids.pop(0)
        await self.storage.pop_chat(mailer_id=self.mailer.id)

    async def sleep(self) -> None:
        with suppress(TimeoutError):
            await wait_for(
                fut=self.stop_event.wait(),
                timeout=self.data.settings.delay,
            )
