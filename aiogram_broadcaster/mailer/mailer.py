from asyncio import Event, TimeoutError, wait_for
from typing import Any, Dict, Iterable, Optional, Set

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from aiogram_broadcaster.contents import BaseContent
from aiogram_broadcaster.event import EventManager
from aiogram_broadcaster.l10n import BaseLanguageGetter
from aiogram_broadcaster.logger import logger
from aiogram_broadcaster.placeholder import PlaceholderWizard
from aiogram_broadcaster.storage.base import BaseBCRStorage

from .chat_engine import ChatEngine, ChatState
from .settings import MailerSettings
from .statistic import MailerStatistic
from .status import MailerStatus
from .tasks import TaskManager


class Mailer:
    _id: int
    _settings: MailerSettings
    _chat_engine: ChatEngine
    _content: BaseContent
    _event: EventManager
    _language_getter: BaseLanguageGetter
    _placeholder: PlaceholderWizard
    _storage: Optional[BaseBCRStorage]
    _mailer_container: Dict[int, "Mailer"]
    _bot: Bot
    _kwargs: Dict[str, Any]
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
        content: BaseContent,
        event: EventManager,
        language_getter: BaseLanguageGetter,
        placeholder: PlaceholderWizard,
        storage: Optional[BaseBCRStorage],
        mailer_container: Dict[int, "Mailer"],
        bot: Bot,
        kwargs: Dict[str, Any],
    ) -> None:
        self._id = id
        self._settings = settings
        self._chat_engine = chat_engine
        self._content = content
        self._event = event
        self._language_getter = language_getter
        self._placeholder = placeholder
        self._storage = storage
        self._mailer_container = mailer_container
        self._bot = bot
        self._kwargs = kwargs
        self._kwargs.update(
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
            f"total_chats={len(self)}"
            ")"
        )

    def __str__(self) -> str:
        return str(self._statistic)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mailer):
            return False
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self._id)

    def __len__(self) -> int:
        return len(self._chat_engine)

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
    def content(self) -> BaseContent:
        return self._content

    @property
    def bot(self) -> Bot:
        return self._bot

    async def add_chats(self, chats: Iterable[int]) -> Set[int]:
        has_difference = await self._chat_engine.add_chats(
            chats=chats,
            state=ChatState.PENDING,
        )
        if has_difference and self._status is MailerStatus.COMPLETED:
            self._status = MailerStatus.STOPPED
        return has_difference

    def start(self, **kwargs: Any) -> None:
        self._check_start()
        self._task.start(self.run(**kwargs))

    async def wait(self) -> None:
        self._check_wait()
        await self._task.wait()

    async def stop(self) -> None:
        self._check_stop()
        await self._emit_stop()

    async def run(self, **kwargs: Any) -> None:
        self._check_start()
        await self._emit_start(**kwargs)
        if await self._broadcast():
            await self._emit_complete()

    async def destroy(self) -> None:
        self._check_destroy()
        await self._emit_destroy()

    def _check_start(self) -> None:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self.id} has been destroyed.")
        if self._status is MailerStatus.STARTED:
            raise RuntimeError(f"Mailer id={self._id} is already started.")
        if self._status is MailerStatus.COMPLETED:
            raise RuntimeError(f"Mailer id={self._id} has been already completed.")

    def _check_stop(self) -> None:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self.id} has been destroyed.")
        if self._status is MailerStatus.STOPPED:
            raise RuntimeError(f"Mailer id={self._id} is already stopped.")
        if self._status is MailerStatus.COMPLETED:
            raise RuntimeError(f"Mailer id={self._id} has been already been completed.")

    def _check_wait(self) -> None:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self.id} has been destroyed.")
        if not self._task.started:
            raise RuntimeError(f"Mailer id={self._id} is not yet started for waiting.")
        if self._task.waited:
            raise RuntimeError(f"Mailer id={self._id} has been already waited.")

    def _check_destroy(self) -> None:
        if self._status is MailerStatus.DESTROYED:
            raise RuntimeError(f"Mailer id={self._id} is already destroyed.")
        if self._id not in self._mailer_container and not self._storage:
            raise RuntimeError(f"Mailer id={self._id} not preserved to destroy.")

    async def _emit_start(self, **kwargs: Any) -> None:
        logger.info("Mailer id=%d started.", self._id)
        self._status = MailerStatus.STARTED
        self._stop_event.clear()
        self._kwargs.update(kwargs)
        if not self._settings.disable_events:
            await self._event.emit_started(**self._kwargs)

    async def _emit_stop(self) -> None:
        logger.info("Mailer id=%d stopped.", self._id)
        self._status = MailerStatus.STOPPED
        self._stop_event.set()
        if not self._settings.disable_events:
            await self._event.emit_stopped(**self._kwargs)

    async def _emit_complete(self) -> None:
        logger.info("Mailer id=%d completed.", self._id)
        self._status = MailerStatus.COMPLETED
        self._stop_event.set()
        if not self._settings.disable_events:
            await self._event.emit_completed(**self._kwargs)
        if self._settings.destroy_on_complete:
            await self._emit_destroy()

    async def _emit_destroy(self) -> None:
        if self._status is MailerStatus.STARTED:
            await self._emit_stop()
        if self._storage:
            await self._storage.delete_record(mailer_id=self._id)
        self._status = MailerStatus.DESTROYED
        self._mailer_container.pop(self._id, None)
        logger.info("Mailer id=%d destroyed.", self._id)

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

    async def send_content(self, chat_id: int) -> Any:
        method = await self._content.as_method(
            chat_id=chat_id,
            language_getter=self._language_getter,
            **self._kwargs,
        )
        if self._settings.exclude_placeholders is not True:
            method = await self._placeholder.render(
                model=method,
                exclude=self._settings.exclude_placeholders,
                chat_id=chat_id,
                **self._kwargs,
            )
        return await method.as_(bot=self._bot)

    async def _send(self, chat_id: int) -> None:
        try:
            response = await self.send_content(chat_id=chat_id)
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
            "Retrying in %.2f seconds. Mailer id=%d, chat id=%d.",
            delay,
            self._id,
            chat_id,
        )
        if await self._sleep(delay=delay):
            await self._send(chat_id=chat_id)

    async def _process_failed_sent(self, chat_id: int, error: Exception) -> None:
        logger.info(
            "Failed to send message. Mailer id=%d, chat id=%d, error: %s.",
            self._id,
            chat_id,
            error,
        )
        await self._chat_engine.set_chat_state(
            chat=chat_id,
            state=ChatState.FAILED,
        )
        if not self._settings.disable_events:
            await self._event.emit_failed_sent(
                chat_id=chat_id,
                error=error,
                **self._kwargs,
            )

    async def _process_success_sent(self, chat_id: int, response: Any) -> None:
        logger.info(
            "Successfully sent. Mailer id=%d, chat id=%d.",
            self._id,
            chat_id,
        )
        await self._chat_engine.set_chat_state(
            chat=chat_id,
            state=ChatState.SUCCESS,
        )
        if not self._settings.disable_events:
            await self._event.emit_success_sent(
                chat_id=chat_id,
                response=response,
                **self._kwargs,
            )

    async def _sleep(self, delay: float) -> bool:
        try:
            await wait_for(
                fut=self._stop_event.wait(),
                timeout=delay,
            )
        except TimeoutError:
            return True
        else:
            return False

    def _resolve_status(self) -> MailerStatus:
        if self._chat_engine.get_chats(ChatState.PENDING):
            return MailerStatus.STOPPED
        return MailerStatus.COMPLETED
