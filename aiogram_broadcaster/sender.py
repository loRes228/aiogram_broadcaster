from asyncio import Event, TimeoutError, wait_for
from typing import TYPE_CHECKING, Any, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from .data import Data
from .event_manager import EventManager
from .logger import logger
from .storage.base import BaseMailerStorage


if TYPE_CHECKING:
    from .mailer import Mailer


class Sender:
    bot: Bot
    mailer: "Mailer"
    data: Data
    storage: BaseMailerStorage
    event: EventManager
    kwargs: Dict[str, Any]
    stop_event: Event
    success_sent: int
    failed_sent: int

    __slots__ = (
        "bot",
        "data",
        "event",
        "failed_sent",
        "kwargs",
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
        kwargs: Dict[str, Any],
    ) -> None:
        self.bot = bot
        self.mailer = mailer
        self.data = data
        self.storage = storage
        self.event = event
        self.kwargs = kwargs

        self.stop_event = Event()
        self.success_sent = 0
        self.failed_sent = 0

        self.stop_event.set()

    async def start(self) -> bool:
        self.stop_event.clear()
        for chat_id in self.data.chat_ids[:]:
            if self.stop_event.is_set():
                break
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self.send(chat_id=chat_id)
            await self.pop_chat()
            if not is_last_chat:
                await self.sleep(delay=self.data.settings.delay)
        else:
            return True
        return False

    def stop(self) -> None:
        self.stop_event.set()

    async def send(self, chat_id: int) -> None:
        try:
            await self.data.settings.message.send(bot=self.bot, chat_id=chat_id)
        except TelegramRetryAfter as error:
            await self.handle_retry_after(chat_id=chat_id, delay=error.retry_after)
        except TelegramAPIError as error:
            await self.handle_failed_sent(chat_id=chat_id, error=error)
        else:
            await self.handle_success_sent(chat_id=chat_id)

    async def handle_retry_after(self, chat_id: int, delay: float) -> None:
        logger.info(
            "Retry after %d seconds for message sent from mailer id=%d to chat id=%d.",
            delay,
            self.mailer.id,
            chat_id,
        )
        if await self.sleep(delay=delay):
            await self.send(chat_id=chat_id)

    async def handle_failed_sent(
        self,
        chat_id: int,
        error: TelegramAPIError,
    ) -> None:
        self.failed_sent += 1
        await self.event.failed_sent.trigger(
            chat_id=chat_id,
            error=error,
            **self.kwargs,
        )
        logger.info(
            "Failed to send message from mailer id=%d to chat id=%d. Error: %s.",
            self.mailer.id,
            chat_id,
            error,
        )

    async def handle_success_sent(self, chat_id: int) -> None:
        self.success_sent += 1
        await self.event.success_sent.trigger(
            chat_id=chat_id,
            **self.kwargs,
        )
        logger.info(
            "Message successfully sent from mailer id=%d to chat id=%d.",
            self.mailer.id,
            chat_id,
        )

    async def pop_chat(self) -> None:
        self.data.chat_ids.pop(0)
        await self.storage.pop_chat(mailer_id=self.mailer.id)

    async def sleep(self, delay: float) -> bool:
        try:
            await wait_for(
                fut=self.stop_event.wait(),
                timeout=delay,
            )
        except TimeoutError:
            return True
        else:
            return False
