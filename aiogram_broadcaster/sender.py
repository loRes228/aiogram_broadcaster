from asyncio import Event, TimeoutError, wait_for
from typing import Any, Dict, Tuple

from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import Message

from .chat_manager import ChatManager, ChatState
from .event_manager import EventManager
from .logger import logger
from .messenger import Messenger
from .settings import MailerSettings


class Sender:
    mailer_id: int
    chat_manager: ChatManager
    event_manager: EventManager
    messenger: Messenger
    settings: MailerSettings
    data: Dict[str, Any]
    stop_event: Event

    __slots__ = (
        "chat_manager",
        "data",
        "event_manager",
        "mailer_id",
        "messenger",
        "settings",
        "stop_event",
    )

    def __init__(
        self,
        mailer_id: int,
        chat_manager: ChatManager,
        event_manager: EventManager,
        messenger: Messenger,
        settings: MailerSettings,
        data: Dict[str, Any],
    ) -> None:
        self.mailer_id = mailer_id
        self.chat_manager = chat_manager
        self.event_manager = event_manager
        self.messenger = messenger
        self.settings = settings
        self.data = data

        self.stop_event = Event()
        self.stop_event.set()

    def stop(self) -> None:
        self.stop_event.set()

    async def start(self) -> bool:
        self.stop_event.clear()
        chats = self.chat_manager.get_chats(state=ChatState.PENDING)
        return await self.broadcast(chat_ids=chats)

    async def broadcast(self, chat_ids: Tuple[int, ...]) -> bool:
        for chat_id in chat_ids:
            if self.stop_event.is_set():
                break
            await self.send(chat_id=chat_id)
            if chat_id != chat_ids[-1]:
                await self.sleep(delay=self.settings.delay)
        else:
            return True
        return False

    async def send(self, chat_id: int) -> None:
        try:
            message = await self.messenger.send(chat_id=chat_id)
        except TelegramRetryAfter as error:
            await self.handle_retry_after(chat_id=chat_id, delay=error.retry_after)
        except TelegramAPIError as error:
            await self.handle_failed_sent(chat_id=chat_id, error=error)
        else:
            await self.handle_success_sent(chat_id=chat_id, message=message)

    async def handle_retry_after(
        self,
        chat_id: int,
        delay: float,
    ) -> None:
        logger.info(
            "Retry after %.2f seconds for message sent from mailer id=%d to chat id=%d.",
            delay,
            self.mailer_id,
            chat_id,
        )
        if await self.sleep(delay=delay):
            await self.send(chat_id=chat_id)

    async def handle_failed_sent(
        self,
        chat_id: int,
        error: TelegramAPIError,
    ) -> None:
        logger.info(
            "Failed to send message from mailer id=%d to chat id=%d. Error: %s.",
            self.mailer_id,
            chat_id,
            error,
        )
        await self.chat_manager.set_state(
            chat=chat_id,
            state=ChatState.FAILED,
        )
        if not self.settings.disable_events:
            await self.event_manager.failed_sent.trigger(
                chat_id=chat_id,
                error=error,
                **self.data,
            )

    async def handle_success_sent(
        self,
        chat_id: int,
        message: Message,
    ) -> None:
        logger.info(
            "Message successfully sent from mailer id=%d to chat id=%d.",
            self.mailer_id,
            chat_id,
        )
        await self.chat_manager.set_state(
            chat=chat_id,
            state=ChatState.SUCCESS,
        )
        if not self.settings.disable_events:
            await self.event_manager.success_sent.trigger(
                chat_id=chat_id,
                message=message,
                **self.data,
            )

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
