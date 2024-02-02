from asyncio import Event, TimeoutError, wait_for
from contextlib import suppress
from logging import Logger
from typing import TYPE_CHECKING, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from .data import Data
from .event import EventManager
from .statistic import Statistic
from .status import Status
from .storage.base import BaseMailerStorage


if TYPE_CHECKING:
    from .pool import MailerPool


class Mailer:
    bot: Bot
    data: Data
    storage: BaseMailerStorage
    event: EventManager
    pool: "MailerPool"
    logger: Logger
    delete_on_complete: bool
    _id: int
    _status: Status
    _stop_event: Event
    _success_sent: int
    _failed_sent: int

    __slots__ = (
        "_failed_sent",
        "_id",
        "_status",
        "_stop_event",
        "_success_sent",
        "bot",
        "data",
        "delete_on_complete",
        "event",
        "logger",
        "pool",
        "storage",
    )

    def __init__(
        self,
        *,
        bot: Bot,
        data: Data,
        storage: BaseMailerStorage,
        event: EventManager,
        pool: "MailerPool",
        delete_on_complete: bool,
        id_: Optional[int] = None,
    ) -> None:
        self.bot = bot
        self.data = data
        self.storage = storage
        self.event = event
        self.pool = pool
        self.delete_on_complete = delete_on_complete

        self._id = id_ or id(self)
        self._status = Status.STOPPED if self.data.chat_ids else Status.COMPLETED
        self._stop_event = Event()
        self._success_sent = 0
        self._failed_sent = 0

        self._stop_event.set()

    def __repr__(self) -> str:
        return "Mailer(id=%d, status=%s, chats_left=%d)" % (
            self._id,
            self._status.value,
            len(self.data.chat_ids),
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
    def status(self) -> Status:
        return self._status

    @property
    def message(self) -> Message:
        return self.data.settings.message.as_(bot=self.bot)

    def statistic(self) -> Statistic:
        return Statistic(
            total_chats=self.data.settings.total_chats,
            success=self._success_sent,
            failed=self._failed_sent,
        )

    async def run(self) -> None:
        if self._status is not Status.STOPPED:
            return
        await self._prepare_run()
        if await self._broadcast():
            await self._process_complete()

    async def stop(self) -> None:
        if self._status is not Status.STARTED:
            return
        await self._stop()

    async def delete(self) -> None:
        if not self.pool.get(id=self._id):
            return
        await self.stop()
        await self._delete()

    async def _prepare_run(self) -> None:
        self._status = Status.STARTED
        self._stop_event.clear()
        await self.event.startup.trigger(mailer=self)

    async def _stop(self) -> None:
        self._status = Status.STOPPED
        self._stop_event.set()
        await self.event.shutdown.trigger(mailer=self)

    async def _delete(self) -> None:
        await self.pool.delete(id=self._id)

    async def _process_complete(self) -> None:
        self._status = Status.COMPLETED
        self._stop_event.set()
        await self.event.complete.trigger(mailer=self)
        if self.delete_on_complete:
            await self._delete()

    async def _broadcast(self) -> bool:
        for chat_id in self.data.chat_ids[:]:
            if self._stop_event.is_set():
                break
            is_last_chat = chat_id == self.data.chat_ids[-1]
            await self._send(chat_id=chat_id)
            await self._pop_chat()
            if not is_last_chat:
                await self._sleep()
        else:
            return True
        return False

    async def _send(self, chat_id: int) -> None:
        try:
            await self.message.send_copy(
                chat_id=chat_id,
                disable_notification=self.data.settings.disable_notification,
                reply_markup=self.data.settings.reply_markup,
            )
        except TelegramAPIError as error:
            await self._handle_failed_sent(chat_id=chat_id, error=error)
        else:
            await self._handle_success_sent(chat_id=chat_id)

    async def _handle_failed_sent(
        self,
        chat_id: int,
        error: TelegramAPIError,
    ) -> None:
        self._failed_sent += 1
        await self.event.failed_sent.trigger(
            mailer=self,
            as_task=True,
            error=error,
            chat_id=chat_id,
        )

    async def _handle_success_sent(self, chat_id: int) -> None:
        self._success_sent += 1
        await self.event.success_sent.trigger(
            mailer=self,
            as_task=True,
            chat_id=chat_id,
        )

    async def _pop_chat(self) -> None:
        self.data.chat_ids.pop(0)
        await self.storage.pop_chat(mailer_id=self._id)

    async def _sleep(self) -> None:
        with suppress(TimeoutError):
            await wait_for(
                fut=self._stop_event.wait(),
                timeout=self.data.settings.delay,
            )
