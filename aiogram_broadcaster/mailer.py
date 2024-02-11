from typing import TYPE_CHECKING, Any, Dict

from aiogram.types import Message

from .chat_manager import ChatManager, ChatState
from .enums import Status, Strategy
from .event_manager import EventManager
from .logger import logger
from .messenger import Messenger
from .sender import Sender
from .settings import ChatIdsType, MailerSettings
from .statistic import Statistic
from .task_manager import TaskManager


if TYPE_CHECKING:
    from .pool import MailerPool


class Mailer:
    _id: int
    _mailer_pool: "MailerPool"
    _task_manager: TaskManager
    _chat_manager: ChatManager
    _event_manager: EventManager
    _messenger: Messenger
    _settings: MailerSettings
    _status: Status
    _data: Dict[str, Any]
    _sender: Sender

    __slots__ = (
        "_chat_manager",
        "_data",
        "_event_manager",
        "_id",
        "_mailer_pool",
        "_messenger",
        "_sender",
        "_settings",
        "_status",
        "_task_manager",
    )

    def __init__(
        self,
        id: int,  # noqa: A002
        mailer_pool: "MailerPool",
        task_manager: TaskManager,
        chat_manager: ChatManager,
        event_manager: EventManager,
        messenger: Messenger,
        settings: MailerSettings,
        data: Dict[str, Any],
    ) -> None:
        self._id = id
        self._mailer_pool = mailer_pool
        self._task_manager = task_manager
        self._chat_manager = chat_manager
        self._event_manager = event_manager
        self._messenger = messenger
        self._settings = settings

        self._status = (
            Status.STOPPED  # fmt: skip
            if chat_manager[ChatState.PENDING]
            else Status.COMPLETED
        )

        self._data = data
        self._data["mailer"] = self

        self._sender = Sender(
            mailer_id=id,
            chat_manager=chat_manager,
            event_manager=event_manager,
            messenger=messenger,
            settings=settings,
            data=self._data,
        )

    def __repr__(self) -> str:
        return "Mailer(id=%d, status=%s)" % (self.id, self.status)

    def __str__(self) -> str:
        return ", ".join(
            f"{key}={value}"  # fmt: skip
            for key, value in self.statistic()._asdict().items()
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def interval(self) -> float:
        return self._settings.delay

    @property
    def status(self) -> Status:
        return self._status

    @property
    def strategy(self) -> Strategy:
        return self._settings.strategy

    @property
    def message(self) -> Message:
        return self._messenger.message

    def statistic(self) -> Statistic:
        return Statistic.from_chat_manager(self._chat_manager)

    async def send(self, chat_id: int) -> Message:
        return await self._messenger.send(chat_id=chat_id)

    async def add_chats(self, chat_ids: ChatIdsType) -> bool:
        is_added = await self._chat_manager.add_chats(chat_ids=chat_ids)
        if is_added and self.status == Status.COMPLETED:
            self._status = Status.STOPPED
        return is_added

    def start(self, **data: Any) -> None:
        if self.status != Status.STOPPED:
            return
        self._task_manager.start(self.run(**data))

    async def wait(self) -> None:
        await self._task_manager.wait()

    async def run(self, **data: Any) -> None:
        if self.status != Status.STOPPED:
            return
        await self._prepare_run(data=data)
        if await self._sender.start():
            await self._process_complete()

    async def stop(self) -> None:
        if self.status != Status.STARTED:
            return
        await self._stop()

    async def delete(self) -> None:
        if not self._mailer_pool.get(mailer_id=self.id):
            return
        await self.stop()
        await self._delete()

    async def _delete(self) -> None:
        await self._mailer_pool.delete(mailer_id=self.id)

    async def _prepare_run(self, data: Dict[str, Any]) -> None:
        logger.info("Mailer id=%d is starting.", self.id)
        self._data.update(data)
        self._status = Status.STARTED
        if not self._settings.disable_events:
            await self._event_manager.startup.trigger(**self._data)

    async def _stop(self) -> None:
        logger.info("Mailer id=%d is stopping.", self.id)
        self._status = Status.STOPPED
        self._sender.stop()
        if not self._settings.disable_events:
            await self._event_manager.shutdown.trigger(**self._data)

    async def _process_complete(self) -> None:
        logger.info("Mailer id=%d has completed successfully.", self.id)
        self._status = Status.COMPLETED
        self._sender.stop()
        if not self._settings.disable_events:
            await self._event_manager.complete.trigger(**self._data)
        if self._settings.delete_on_complete:
            await self._delete()
