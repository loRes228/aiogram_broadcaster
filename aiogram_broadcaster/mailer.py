from typing import TYPE_CHECKING, Optional

from aiogram import Bot
from aiogram.types import Message

from .data import Data
from .event_manager import EventManager
from .sender import Sender
from .statistic import Statistic
from .status import Status
from .storage.base import BaseMailerStorage
from .task_manager import TaskManager


if TYPE_CHECKING:
    from .pool import MailerPool


class Mailer:
    data: Data
    event: EventManager
    pool: "MailerPool"
    delete_on_complete: bool
    _id: int
    _status: Status
    _task: TaskManager
    _sender: Sender

    __slots__ = (
        "_id",
        "_sender",
        "_status",
        "_task",
        "data",
        "delete_on_complete",
        "event",
        "pool",
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
        self.data = data
        self.event = event
        self.pool = pool
        self.delete_on_complete = delete_on_complete

        self._id = id_ or id(self)
        self._status = Status.STOPPED if self.data.chat_ids else Status.COMPLETED
        self._task = TaskManager()
        self._sender = Sender(
            bot=bot,
            mailer=self,
            data=data,
            storage=storage,
            event=event,
        )

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
        return self._sender.message

    def statistic(self) -> Statistic:
        return Statistic(
            total_chats=self.data.settings.total_chats,
            success=self._sender.success_sent,
            failed=self._sender.failed_sent,
        )

    def start(self) -> None:
        self._task.start(callback=self.run)

    async def wait(self) -> None:
        await self._task.wait()

    async def run(self) -> None:
        if self._status is not Status.STOPPED:
            return
        await self._prepare_run()
        if await self._sender.start():
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
        await self.event.startup.trigger(mailer=self)

    async def _stop(self) -> None:
        self._status = Status.STOPPED
        self._sender.stop()
        await self.event.shutdown.trigger(mailer=self)

    async def _process_complete(self) -> None:
        self._status = Status.COMPLETED
        self._sender.stop()
        await self.event.complete.trigger(mailer=self)
        if self.delete_on_complete:
            await self._delete()

    async def _delete(self) -> None:
        await self.pool.delete(id=self._id)
