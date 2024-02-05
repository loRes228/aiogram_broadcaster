from typing import TYPE_CHECKING, Any, Dict, Optional

from aiogram import Bot
from aiogram.types import Message

from .data import Data
from .event_manager import EventManager
from .logger import logger
from .sender import Sender
from .statistic import Statistic
from .status import Status
from .storage.base import BaseMailerStorage
from .task_manager import TaskManager


if TYPE_CHECKING:
    from .pool import MailerPool


class Mailer:
    bot: Bot
    data: Data
    event: EventManager
    pool: "MailerPool"
    kwargs: Dict[str, Any]
    _id: int
    _status: Status
    _task: TaskManager
    _sender: Sender

    __slots__ = (
        "_id",
        "_sender",
        "_status",
        "_task",
        "bot",
        "data",
        "event",
        "kwargs",
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
        id_: Optional[int] = None,
        kwargs: Dict[str, Any],
    ) -> None:
        self.bot = bot
        self.data = data
        self.event = event
        self.pool = pool
        self.kwargs = kwargs

        self._id = id_ or id(self)
        self._status = Status.STOPPED if self.data.chat_ids else Status.COMPLETED
        self._task = TaskManager()

        self.kwargs["mailer"] = self
        self._sender = Sender(
            bot=bot,
            mailer=self,
            data=data,
            storage=storage,
            event=event,
            kwargs=self.kwargs,
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
        return self.data.settings.message.object.as_(bot=self.bot)

    def statistic(self) -> Statistic:
        return Statistic(
            total_chats=self.data.settings.total_chats,
            success=self._sender.success_sent,
            failed=self._sender.failed_sent,
        )

    def start(self) -> None:
        self._task.start(self.run())

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
        await self.event.startup.trigger(**self.kwargs)
        logger.info("Mailer id=%d is starting.", self._id)

    async def _stop(self) -> None:
        self._status = Status.STOPPED
        self._sender.stop()
        await self.event.shutdown.trigger(**self.kwargs)
        logger.info("Mailer id=%d is stopping.", self._id)

    async def _process_complete(self) -> None:
        self._status = Status.COMPLETED
        self._sender.stop()
        await self.event.complete.trigger(**self.kwargs)
        if self.data.settings.delete_on_complete:
            await self._delete()
        logger.info("Mailer id=%d has completed successfully.", self._id)

    async def _delete(self) -> None:
        await self.pool.delete(id=self._id)
