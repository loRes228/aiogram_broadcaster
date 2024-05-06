from asyncio import Event, TimeoutError, wait_for
from typing import Any, Dict, Generic, Iterable, Optional, Set

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from aiogram_broadcaster import loggers
from aiogram_broadcaster.contents.base import ContentType
from aiogram_broadcaster.event import EventManager
from aiogram_broadcaster.placeholder import PlaceholderManager
from aiogram_broadcaster.storage.base import BaseMailerStorage

from .chat_engine import ChatEngine, ChatsRegistry, ChatState
from .settings import MailerSettings
from .statistic import MailerStatistic
from .status import MailerStatus
from .task_manager import TaskManager


class Mailer(Generic[ContentType]):
    _id: int
    _settings: MailerSettings
    _content: ContentType
    _event: EventManager
    _placeholder: PlaceholderManager
    _storage: Optional[BaseMailerStorage]
    _mailer_container: Dict[int, "Mailer"]
    _bot: Bot
    _context: Dict[str, Any]
    _chat_engine: ChatEngine
    _statistic: MailerStatistic
    _task_manager: TaskManager
    _status: MailerStatus
    _stop_event: Event

    def __init__(
        self,
        *,
        id: int,  # noqa: A002
        settings: MailerSettings,
        chats: ChatsRegistry,
        content: ContentType,
        event: EventManager,
        placeholder: PlaceholderManager,
        storage: Optional[BaseMailerStorage],
        mailer_container: Dict[int, "Mailer"],
        bot: Bot,
        context: Dict[str, Any],
    ) -> None:
        self._id = id
        self._settings = settings
        self._content = content
        self._event = event
        self._placeholder = placeholder
        self._storage = storage
        self._mailer_container = mailer_container
        self._bot = bot
        self._context = context
        self._context.update(mailer=self, bot=self._bot)

        self._chat_engine = ChatEngine(registry=chats, mailer_id=self._id, storage=self._storage)
        self._statistic = MailerStatistic(chat_engine=self._chat_engine)
        self._task_manager = TaskManager()
        self._status = self._resolve_status()
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
    def context(self) -> Dict[str, Any]:
        return self._context

    @property
    def bot(self) -> Bot:
        return self._bot

    async def send(self, chat_id: int) -> Any:
        method = await self._content.as_method(chat_id=chat_id, **self._context)
        if self._settings.exclude_placeholders is not True:
            method = await self._placeholder.render(
                method,
                self._settings.exclude_placeholders,
                chat_id=chat_id,
                **self._context,
            )
        return await method.as_(bot=self._bot)

    async def add_chats(self, chats: Iterable[int]) -> Set[int]:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self._id} cant be added the chats.")
        new_chats = await self._chat_engine.add_chats(chats=chats, state=ChatState.PENDING)
        if not new_chats:
            return set()
        if self._status is MailerStatus.COMPLETED:
            self._status = MailerStatus.STOPPED
        loggers.mailer.info("Mailer id=%d new %d chats added.", self._id, len(new_chats))
        return new_chats

    async def reset_chats(self) -> bool:
        if self._status in {MailerStatus.STARTED, MailerStatus.DESTROYED}:
            raise RuntimeError(f"Mailer id={self._id} cant be reset.")
        is_reset = await self._chat_engine.set_chats_state(state=ChatState.PENDING)
        if not is_reset:
            return False
        if self._status is MailerStatus.COMPLETED:
            self._status = MailerStatus.STOPPED
        loggers.mailer.info("Mailer id=%d has been reset.", self._id)
        return is_reset

    async def destroy(self) -> None:
        if self._status in {MailerStatus.STARTED, MailerStatus.DESTROYED}:
            raise RuntimeError(f"Mailer id={self._id} cant be destroyed.")
        loggers.mailer.info("Mailer id=%d has been destroyed.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.DESTROYED
        if not self._settings.preserved:
            return
        del self._mailer_container[self._id]
        if self._storage:
            await self._storage.delete(mailer_id=self._id)

    async def stop(self) -> None:
        if self._status is not MailerStatus.STARTED:
            raise RuntimeError(f"Mailer id={self._id} cant be stopped.")
        loggers.mailer.info("Mailer id=%d is stopped.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.STOPPED
        if not self._settings.disable_events:
            await self._event.emit_stopped(**self._context)

    async def run(self) -> bool:
        if self._status is not MailerStatus.STOPPED:
            raise RuntimeError(f"Mailer id={self._id} cant be started.")
        loggers.mailer.info("Mailer id=%d is started.", self._id)
        self._stop_event.clear()
        self._status = MailerStatus.STARTED
        if not self._settings.disable_events:
            await self._event.emit_started(**self._context)
        try:
            completed = await self._broadcast()
        except:
            await self.stop()
            raise
        if not completed:
            return False
        loggers.mailer.info("Mailer id=%d successfully completed.", self._id)
        self._stop_event.set()
        self._status = MailerStatus.COMPLETED
        if self._settings.destroy_on_complete:
            await self.destroy()
        if not self._settings.disable_events:
            await self._event.emit_completed(**self._context)
        return True

    def start(self) -> None:
        if self._status is not MailerStatus.STOPPED:
            raise RuntimeError(f"Mailer id={self._id} cant be started.")
        self._task_manager.start(target=self.run())

    async def wait(self) -> None:
        if not self._task_manager.started or self._task_manager.waited:
            raise RuntimeError(f"Mailer id={self._id} cant be wait.")
        await self._task_manager.wait()

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
        if not self._settings.disable_events:
            await self._event.emit_before_sent(chat_id=chat_id, **self._context)
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
        loggers.mailer.info(
            "Mailer id=%d waits %.2f seconds to resend a message to chat id=%d.",
            self._id,
            delay,
            chat_id,
        )
        if await self._sleep(delay=delay):
            await self._send(chat_id=chat_id)

    async def _process_failed_sent(self, chat_id: int, error: Exception) -> None:
        loggers.mailer.info(
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
                **self._context,
            )

    async def _process_success_sent(self, chat_id: int, response: Any) -> None:
        loggers.mailer.info(
            "Mailer id=%d successfully sent a message to chat id=%d.",
            self._id,
            chat_id,
        )
        await self._chat_engine.set_chat_state(chat=chat_id, state=ChatState.SUCCESS)
        if not self._settings.disable_events:
            await self._event.emit_success_sent(
                chat_id=chat_id,
                response=response,
                **self._context,
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
