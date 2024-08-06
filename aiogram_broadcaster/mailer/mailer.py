from asyncio import Event, Task, create_task
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Optional, cast

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from pydantic import JsonValue
from typing_extensions import Self

from aiogram_broadcaster.contents.base import ContentType
from aiogram_broadcaster.intervals.base import BaseInterval
from aiogram_broadcaster.storages.base import StorageRecord
from aiogram_broadcaster.utils.exceptions import (
    MailerDestroyedError,
    MailerExtendedError,
    MailerResetError,
    MailerStartedError,
    MailerStoppedError,
)
from aiogram_broadcaster.utils.id_generator import generate_id
from aiogram_broadcaster.utils.logger import logger

from .chats import Chats, ChatState
from .status import MailerStatus


if TYPE_CHECKING:
    from aiogram.methods import TelegramMethod

    from aiogram_broadcaster.broadcaster import Broadcaster


@dataclass
class Mailer(Generic[ContentType]):
    id: int
    status: MailerStatus
    chats: Chats
    content: ContentType
    interval: Optional[BaseInterval]
    bot: Bot
    context: dict[str, Any]
    broadcaster: "Broadcaster"
    _stop_event: Event
    _destroyed: bool

    @classmethod
    async def create(
        cls,
        broadcaster: "Broadcaster",
        chats: Iterable[int],
        content: ContentType,
        bot: Optional[Bot] = None,
        interval: Optional[BaseInterval] = None,
        **context: JsonValue,
    ) -> Self:
        if not chats:
            raise ValueError("At least one chat must be provided.")
        if not bot and not broadcaster.bots:
            raise ValueError("At least one bot must be provided.")
        mailer_id: int = generate_id(container=broadcaster)
        chats_ = Chats.from_iterable(iterable=chats)
        bot = bot or broadcaster.bots[-1]
        stop_event = Event()
        stop_event.set()
        mailer = cls(
            id=mailer_id,
            status=MailerStatus.STOPPED,
            chats=chats_,
            content=content,
            interval=interval,
            bot=bot,
            context=context.copy(),
            broadcaster=broadcaster,
            _stop_event=stop_event,
            _destroyed=False,
        )
        mailer.context.update(
            broadcaster.context,
            mailer=mailer,
            bot=bot,
        )
        record = StorageRecord(
            chats=chats_,
            content=content,
            interval=interval,
            bot_id=bot.id,
            context=context,
        )
        if broadcaster.storage:
            await broadcaster.storage.set_record(mailer_id=mailer.id, record=record)
        broadcaster.mailers[mailer.id] = cast(Mailer, mailer)
        logger.info("Mailer id=%d was created.", mailer.id)
        await broadcaster.event.emit_created(**mailer.context)
        return mailer

    @classmethod
    async def create_from_record(
        cls,
        broadcaster: "Broadcaster",
        mailer_id: int,
        record: StorageRecord,
    ) -> Self:
        try:
            bot: Bot = {bot.id: bot for bot in broadcaster.bots}[record.bot_id]
        except KeyError as error:
            raise LookupError(
                f"Mailer id {mailer_id} could not find bot with id {record.bot_id}, "
                f"add the bot instance to Broadcaster.",
            ) from error
        status = (
            MailerStatus.STOPPED
            if record.chats.registry[ChatState.PENDING]
            else MailerStatus.COMPLETED
        )
        stop_event = Event()
        stop_event.set()
        mailer = cls(
            id=mailer_id,
            status=status,
            chats=record.chats,
            content=cast(ContentType, record.content),
            interval=record.interval,
            bot=bot,
            context=record.context.copy(),
            broadcaster=broadcaster,
            _stop_event=stop_event,
            _destroyed=False,
        )
        mailer.context.update(
            broadcaster.context,
            mailer=mailer,
            bot=bot,
        )
        broadcaster.mailers[mailer.id] = cast(Mailer, mailer)
        logger.info("Mailer id=%d was restored from storage.", mailer.id)
        await broadcaster.event.emit_created(**mailer.context)
        return mailer

    def __repr__(self) -> str:
        return f"Mailer(id={self.id}, status='{self.status.name.lower()}')"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mailer):
            return NotImplemented
        return hash(self) == hash(other)

    async def destroy(self) -> None:
        if self._destroyed:
            raise MailerDestroyedError(mailer_id=self.id)
        logger.info("Mailer id=%d was destroyed.", self.id)
        self.status = MailerStatus.COMPLETED
        self._stop_event.set()
        del self.broadcaster.mailers[self.id]
        if self.broadcaster.storage:
            await self.broadcaster.storage.delete_record(mailer_id=self.id)
        await self.broadcaster.event.emit_destroyed(**self.context)

    async def stop(self) -> None:
        if self.status is not MailerStatus.STARTED:
            raise MailerStoppedError(mailer_id=self.id)
        logger.info("Mailer id=%d was stopped.", self.id)
        self.status = MailerStatus.STOPPED
        self._stop_event.set()
        await self.broadcaster.event.emit_stopped(**self.context)

    def start(self) -> Task[bool]:
        return create_task(coro=self._start())

    async def _start(self) -> bool:
        if self.status is not MailerStatus.STOPPED:
            raise MailerStartedError(mailer_id=self.id)
        logger.info("Mailer id=%d was started.", self.id)
        self.status = MailerStatus.STARTED
        self._stop_event.clear()
        await self.broadcaster.event.emit_started(**self.context)
        try:
            completed = await self._process_chats()
        except:
            await self.stop()
            raise
        if not completed:
            return False
        logger.info("Mailer id=%d was completed.", self.id)
        self.status = MailerStatus.COMPLETED
        self._stop_event.set()
        await self.broadcaster.event.emit_completed(**self.context)
        return True

    async def extend(self, chats: Iterable[int]) -> set[int]:
        if self._destroyed:
            raise MailerExtendedError(mailer_id=self.id)
        difference: set[int] = set(chats) - self.chats.total.ids
        if not difference:
            return difference
        self.chats.registry[ChatState.PENDING].update(difference)
        if self.broadcaster.storage:
            async with self.broadcaster.storage.update_record(mailer_id=self.id) as record:
                record.chats = self.chats
        if self.status is MailerStatus.COMPLETED:
            self.status = MailerStatus.STOPPED
        logger.info(
            "Mailer id=%d has been updated with %d new chats.",
            self.id,
            len(difference),
        )
        return difference

    async def reset(self) -> None:
        if self._destroyed or self.status is MailerStatus.STARTED:
            raise MailerResetError(mailer_id=self.id)
        total_chats: set[int] = self.chats.total.ids
        if self.chats.registry[ChatState.PENDING] == total_chats:
            raise MailerResetError(mailer_id=self.id)
        self.chats.registry.clear()
        self.chats.registry[ChatState.PENDING].update(total_chats)
        if self.broadcaster.storage:
            async with self.broadcaster.storage.update_record(mailer_id=self.id) as record:
                record.chats = self.chats
        if self.status is MailerStatus.COMPLETED:
            self.status = MailerStatus.STOPPED
        logger.info("Mailer id=%d has been reset.")

    async def send(
        self,
        chat_id: int,
        *,
        disable_placeholders: bool = False,
        disable_error_handling: bool = False,
    ) -> tuple[bool, Any]:
        method: TelegramMethod[Any] = await self.content.as_method(
            chat_id=chat_id,
            **self.context,
        )
        method.as_(bot=self.bot)
        if not disable_placeholders:
            method = await self.broadcaster.placeholder.render(
                method,
                chat_id=chat_id,
                **self.context,
            )
        if disable_error_handling:
            return True, await method
        try:
            response: Any = await method
        except TelegramAPIError as error:
            logger.info(
                "Mailer id=%d failed send the content to chat id=%d due to: %s.",
                self.id,
                chat_id,
                error,
            )
            await self.broadcaster.event.emit_failed_send(
                chat_id=chat_id,
                error=error,
                **self.context,
            )
            return False, error
        else:
            logger.info(
                "Mailer id=%d success send the content to chat id=%d.",
                self.id,
                chat_id,
            )
            await self.broadcaster.event.emit_success_send(
                chat_id=chat_id,
                response=response,
                **self.context,
            )
            return True, response

    async def _process_chats(self) -> bool:
        while self.chats.registry[ChatState.PENDING]:
            if self._stop_event.is_set():
                return False
            chat: int = self.chats.registry[ChatState.PENDING].pop()
            success, _ = await self.send(chat_id=chat)
            self.chats.registry[ChatState.SUCCESS if success else ChatState.FAILED].add(chat)
            if self.broadcaster.storage:
                async with self.broadcaster.storage.update_record(mailer_id=self.id) as record:
                    record.chats = self.chats
            if not self.chats.registry[ChatState.PENDING]:
                return True
            if self.interval:
                await self.interval.sleep(self._stop_event, **self.context)
        return True
