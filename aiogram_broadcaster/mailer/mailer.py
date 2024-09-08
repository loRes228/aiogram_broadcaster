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
    MailerDeleteError,
    MailerExtendError,
    MailerResetError,
    MailerStartError,
    MailerStopError,
)
from aiogram_broadcaster.utils.id_generator import generate_id
from aiogram_broadcaster.utils.logger import logger

from .chats import Chats, ChatState
from .status import MailerStatus


if TYPE_CHECKING:
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
    _deleted: bool

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
        mailer_id = generate_id(container=broadcaster)
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
            _deleted=False,
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
            bot = {bot.id: bot for bot in broadcaster.bots}[record.bot_id]
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
            _deleted=False,
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

    @property
    def can_deleted(self) -> bool:
        return not self._deleted

    @property
    def can_stopped(self) -> bool:
        return not self._deleted and self.status is MailerStatus.STARTED

    @property
    def can_started(self) -> bool:
        return not self._deleted and self.status is MailerStatus.STOPPED

    @property
    def can_extended(self) -> bool:
        return not self._deleted

    @property
    def can_reset(self) -> bool:
        return (
            not self._deleted
            and self.status is not MailerStatus.STARTED
            and self.chats.total != self.chats.pending
        )

    async def delete(self) -> None:
        if not self.can_deleted:
            raise MailerDeleteError(mailer_id=self.id)
        logger.info("Mailer id=%d was deleted.", self.id)
        self.status = MailerStatus.COMPLETED
        self._stop_event.set()
        self._deleted = True
        del self.broadcaster.mailers[self.id]
        if self.broadcaster.storage:
            await self.broadcaster.storage.delete_record(mailer_id=self.id)
        await self.broadcaster.event.emit_deleted(**self.context)

    async def stop(self) -> None:
        if not self.can_stopped:
            raise MailerStopError(mailer_id=self.id)
        logger.info("Mailer id=%d was stopped.", self.id)
        self.status = MailerStatus.STOPPED
        self._stop_event.set()
        await self.broadcaster.event.emit_stopped(**self.context)

    def start(self) -> Task[bool]:
        return create_task(coro=self._start())

    async def _start(self) -> bool:
        if not self.can_started:
            raise MailerStartError(mailer_id=self.id)
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
        if not self.can_extended:
            raise MailerExtendError(mailer_id=self.id)
        difference = set(chats) - self.chats.total.ids
        if not difference:
            return difference
        self.chats.registry[ChatState.PENDING].update(difference)
        await self._preserve_chats()
        if self.status is MailerStatus.COMPLETED:
            self.status = MailerStatus.STOPPED
        logger.info(
            "Mailer id=%d has been updated with %d new chats.",
            self.id,
            len(difference),
        )
        return difference

    async def reset(self) -> None:
        if not self.can_reset:
            raise MailerResetError(mailer_id=self.id)
        total_chats = self.chats.total.ids
        self.chats.registry.clear()
        self.chats.registry[ChatState.PENDING].update(total_chats)
        await self._preserve_chats()
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
        method = await self.content.as_method(
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
            response = await method
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
            chat = self.chats.registry[ChatState.PENDING].pop()
            success, _ = await self.send(chat_id=chat)
            self.chats.registry[ChatState.SUCCESS if success else ChatState.FAILED].add(chat)
            await self._preserve_chats()
            if not self.chats.registry[ChatState.PENDING]:
                return True
            if self.interval:
                await self.interval.sleep(self._stop_event, **self.context)
        return True

    async def _preserve_chats(self) -> None:
        if self.broadcaster.storage:
            async with self.broadcaster.storage.update_record(mailer_id=self.id) as record:
                record.chats = self.chats
