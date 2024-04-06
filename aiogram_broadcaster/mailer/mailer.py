from asyncio import Event, TimeoutError, wait_for
from typing import Any, Dict, Generic, Iterable, Optional, Set

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from aiogram_broadcaster.contents.base import ContentType
from aiogram_broadcaster.event import EventManager
from aiogram_broadcaster.logger import logger
from aiogram_broadcaster.placeholder import PlaceholderWizard
from aiogram_broadcaster.storage.base import BaseBCRStorage

from .chat_engine import ChatEngine, ChatState
from .settings import MailerSettings
from .statistic import MailerStatistic
from .status import MailerStatus
from .tasks import TaskManager


class Mailer(Generic[ContentType]):
    _id: int
    _settings: MailerSettings
    _chat_engine: ChatEngine
    _content: ContentType
    _event: EventManager
    _placeholder: PlaceholderWizard
    _storage: Optional[BaseBCRStorage]
    _mailer_container: Dict[int, "Mailer"]
    _bot: Bot
    _contextual_data: Dict[str, Any]
    _status: MailerStatus
    _statistic: MailerStatistic
    _task: TaskManager
    _stop_event: Event

    def __init__(
        self,
        *,
        id: int,  # noqa: A002
        settings: MailerSettings,
        chat_engine: ChatEngine,
        content: ContentType,
        event: EventManager,
        placeholder: PlaceholderWizard,
        storage: Optional[BaseBCRStorage],
        mailer_container: Dict[int, "Mailer"],
        bot: Bot,
        contextual_data: Dict[str, Any],
    ) -> None:
        self._id = id
        self._settings = settings
        self._chat_engine = chat_engine
        self._content = content
        self._event = event
        self._placeholder = placeholder
        self._storage = storage
        self._mailer_container = mailer_container
        self._bot = bot
        self._contextual_data = contextual_data
        self._contextual_data.update(
            mailer=self,
            bot=bot,
        )

        self._status = self._resolve_status()
        self._statistic = MailerStatistic(chat_engine=self._chat_engine)
        self._task = TaskManager()
        self._stop_event = Event()
        self._stop_event.set()

    def __repr__(self) -> str:
        return (
            f"Mailer("
            f"id={self._id}, "
            f"status={self._status.name.lower()!r}, "
            f"interval={self._settings.interval:.2f}, "
            f"chats={self._statistic.processed_chats.total}/{self._statistic.total_chats.total}"
            ")"
        )

    def __str__(self) -> str:
        return str(self._statistic)

    def __bool__(self) -> bool:
        return self._status is MailerStatus.COMPLETED

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mailer):
            return False
        return hash(self) == hash(other)

    @property
    def id(self) -> int:
        return self._id

    @property
    def status(self) -> MailerStatus:
        return self._status

    @property
    def settings(self) -> MailerSettings:
        return self._settings

    @property
    def statistic(self) -> MailerStatistic:
        return self._statistic

    @property
    def content(self) -> ContentType:
        return self._content

    @property
    def bot(self) -> Bot:
        return self._bot

    async def send(self, chat_id: int) -> Any:
        method = await self._content.as_method(chat_id=chat_id, **self._contextual_data)
        if self._settings.exclude_placeholders is not True:
            method = await self._placeholder.render(
                model=method,
                exclude=self._settings.exclude_placeholders,
                chat_id=chat_id,
                **self._contextual_data,
            )
        return await method.as_(bot=self.bot)

    async def add_chats(self, chats: Iterable[int]) -> Set[int]:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self._id} cant be added the chats.")
        new_chats = await self._chat_engine.add_chats(chats=chats, state=ChatState.PENDING)
        if new_chats:
            if self._status is MailerStatus.COMPLETED:
                self._status = MailerStatus.STOPPED
            logger.info("Mailer id=%d new %d chats added.", self._id, len(new_chats))
        return new_chats

    async def reset_chats(self) -> None:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self._id} cant be reset.")
        await self._chat_engine.set_chats_state(state=ChatState.PENDING)
        if self._status is MailerStatus.COMPLETED:
            self._status = MailerStatus.STOPPED
        logger.info("Mailer id=%d has been reset.", self._id)

    async def destroy(self) -> None:
        if self._status is MailerStatus.DESTROYED or self._status is MailerStatus.STARTED:
            raise RuntimeError(f"Mailer id={self._id} cant be destroyed.")
        logger.info("Mailer id=%d has been destroyed.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.DESTROYED
        if not self._settings.preserved:
            return
        del self._mailer_container[self._id]
        if self._storage:
            await self._storage.delete_record(mailer_id=self._id)

    async def stop(self) -> None:
        if self._status is not MailerStatus.STARTED:
            raise RuntimeError(f"Mailer id={self._id} cant be stopped.")
        logger.info("Mailer id=%d is stopped.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.STOPPED
        if not self._settings.disable_events:
            await self._event.emit_stopped(**self._contextual_data)

    async def run(self) -> None:
        if self._status is not MailerStatus.STOPPED:
            raise RuntimeError(f"Mailer id={self._id} cant be started.")
        logger.info("Mailer id=%d is started.", self._id)
        self._stop_event.clear()
        self._status = MailerStatus.STARTED
        if not self._settings.disable_events:
            await self._event.emit_started(**self._contextual_data)
        try:
            completed = await self._broadcast()
        except:
            await self.stop()
            raise
        if not completed:
            return
        logger.info("Mailer id=%d successfully completed.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.COMPLETED
        if not self._settings.disable_events:
            await self._event.emit_completed(**self._contextual_data)
        if self._settings.destroy_on_complete:
            await self.destroy()

    def start(self) -> None:
        if self._status is not MailerStatus.STOPPED:
            raise RuntimeError(f"Mailer id={self._id} cant be started.")
        self._task.start(self.run())

    async def wait(self) -> None:
        if not self._task.started or self._task.waited:
            raise RuntimeError(f"Mailer id={self._id} cant be wait.")
        await self._task.wait()

    async def _broadcast(self) -> bool:
        async for chat in self._chat_engine.iterate_chats(state=ChatState.PENDING):
            if self._stop_event.is_set():
                return False
            await self._send(chat_id=chat)
            if not self._chat_engine.get_chats(ChatState.PENDING):
                return True
            if not self._settings.interval:
                continue
            if not await self._sleep(delay=self._settings.interval):
                return False
        return True

    async def _send(self, chat_id: int) -> None:
        try:
            response = await self.send(chat_id=chat_id)
        except TelegramRetryAfter as error:
            if self._settings.handle_retry_after:
                await self._process_retry_after(chat_id=chat_id, delay=error.retry_after)
            else:
                await self._process_failed_sent(chat_id=chat_id, error=error)
        except TelegramAPIError as error:
            await self._process_failed_sent(chat_id=chat_id, error=error)
        else:
            await self._process_success_sent(chat_id=chat_id, response=response)

    async def _process_retry_after(self, chat_id: int, delay: float) -> None:
        logger.info(
            "Mailer id=%d waits %.2f seconds to resend a message to chat id=%d.",
            self._id,
            delay,
            chat_id,
        )
        if await self._sleep(delay=delay):
            await self._send(chat_id=chat_id)

    async def _process_failed_sent(self, chat_id: int, error: Exception) -> None:
        logger.info(
            "Mailer id=%d failed to send a message to chat id=%d, error: %s.",
            self._id,
            chat_id,
            error,
        )
        await self._chat_engine.set_chat_state(chat=chat_id, state=ChatState.FAILED)
        if not self._settings.disable_events:
            await self._event.emit_failed_sent(
                chat_id=chat_id,
                error=error,
                **self._contextual_data,
            )

    async def _process_success_sent(self, chat_id: int, response: Any) -> None:
        logger.info(
            "Mailer id=%d successfully sent a message to chat id=%d.",
            self._id,
            chat_id,
        )
        await self._chat_engine.set_chat_state(chat=chat_id, state=ChatState.SUCCESS)
        if not self._settings.disable_events:
            await self._event.emit_success_sent(
                chat_id=chat_id,
                response=response,
                **self._contextual_data,
            )

    async def _sleep(self, delay: float) -> bool:
        try:
            await wait_for(fut=self._stop_event.wait(), timeout=delay)
        except TimeoutError:
            return True
        else:
            return False

    def _resolve_status(self) -> MailerStatus:
        if self._chat_engine.get_chats(ChatState.PENDING):
            return MailerStatus.STOPPED
        return MailerStatus.COMPLETED
