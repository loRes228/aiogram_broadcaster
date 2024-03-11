from datetime import timedelta
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from aiogram import Bot, Dispatcher

from .contents import BaseContent
from .event import EventRouter
from .l10n import BaseLanguageGetter, L10nContentAdapter
from .logger import logger
from .mailer import Mailer, MailerStatus
from .mailer.chat_manager import ChatManager, ChatState
from .mailer.settings import MailerSettings
from .storage.base import BaseBCRStorage, DataComposer
from .utils.id import generate_id


class Broadcaster:
    _bots: Dict[int, Bot]
    storage: Optional[BaseBCRStorage]
    language_getter: Optional[BaseLanguageGetter]
    context_key: str
    run_on_startup: bool
    kwargs: Dict[str, Any]
    event: EventRouter
    _mailers: Dict[int, Mailer]

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseBCRStorage] = None,
        language_getter: Optional[BaseLanguageGetter] = None,
        context_key: str = "broadcaster",
        run_on_startup: bool = False,
        delete_on_complete: bool = False,
        handle_retry_after: bool = False,
        **kwargs: Any,
    ) -> None:
        self._bots = {bot.id: bot for bot in bots}
        self.storage = storage
        self.language_getter = language_getter
        self.context_key = context_key
        self.run_on_startup = run_on_startup
        self.delete_on_complete = delete_on_complete
        self.handle_retry_after = handle_retry_after
        self.kwargs = kwargs
        self.kwargs["broadcaster"] = self

        self.event = EventRouter()
        self._mailers = {}

        if self.delete_on_complete:
            self._apply_delete_on_complete()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(total_mailers={len(self)})"

    def __str__(self) -> str:
        return f"{type(self).__name__}[{', '.join(map(repr, self))}]"

    def __contains__(self, item: Mailer) -> bool:
        return item in self._mailers.values()

    def __getitem__(self, item: int) -> Mailer:
        if mailer := self._mailers.get(item):
            return mailer
        raise LookupError(f"Mailer with id={item} not exists.")

    def __iter__(self) -> Iterator[Mailer]:
        return iter(self._mailers.values())

    def __len__(self) -> int:
        return len(self._mailers)

    @property
    def bots(self) -> Tuple[Bot, ...]:
        return tuple(self._bots.values())

    @property
    def mailers(self) -> List[Mailer]:
        return list(self._mailers.values())

    def get_mailer(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    def include_event(self, event: EventRouter) -> None:
        self.event.include_event(event=event)

    def include_events(self, *events: EventRouter) -> None:
        if not events:
            raise ValueError("At least one event must be provided.")
        for event in events:
            self.include_event(event=event)

    async def delete_mailer(self, mailer_id: int) -> None:
        mailer = self[mailer_id]
        if mailer.status is MailerStatus.STARTED:
            await mailer.stop()
        if mailer.settings.preserved and self.storage:
            await self.storage.delete(mailer_id=mailer_id)
        del self._mailers[mailer_id]
        mailer._deleted = True  # noqa: SLF001

    async def create_mailer(
        self,
        content: BaseContent,
        chats: Iterable[int],
        *,
        bot: Optional[Bot] = None,
        interval: Union[float, timedelta] = 1,
        dynamic_interval: bool = False,
        disable_events: bool = False,
        preserve: bool = True,
        **kwargs: Any,
    ) -> Mailer:
        if not bot and not self._bots:
            raise ValueError("At least one bot must be provided.")
        if isinstance(content, L10nContentAdapter) and not self.language_getter:
            raise RuntimeError("To use 'L10nContentAdapter' language_getter must be specified.")

        if not bot:
            bot = self.bots[-1]
        else:
            self._bots[bot.id] = bot

        if isinstance(interval, timedelta):
            interval = interval.total_seconds()
        if dynamic_interval:
            interval = interval / len(set(chats))

        mailer_id = generate_id(container=self._mailers)
        settings = MailerSettings(
            interval=interval,
            disable_events=disable_events,
            preserved=preserve,
        )
        chat_manager = ChatManager.from_iterable(
            iterable=chats,
            state=ChatState.PENDING,
            mailer_id=mailer_id,
            storage=self.storage if preserve else None,
        )
        mailer = Mailer(
            id=mailer_id,
            settings=settings,
            chat_manager=chat_manager,
            content=content,
            event=self.event,
            language_getter=self.language_getter,
            bot=bot,
            handle_retry_after=self.handle_retry_after,
            kwargs={**self.kwargs, **kwargs},
        )
        if not preserve:
            return mailer
        self._mailers[mailer_id] = mailer
        if self.storage:
            data = DataComposer(
                content=content,
                chat_manager=chat_manager,
                settings=settings,
                bot_id=bot.id,
            )
            await self.storage.set_data(mailer_id=mailer_id, data=data)
        return mailer

    async def restore_mailers(self) -> None:
        if not self.storage:
            raise RuntimeError("Storage not specified.")
        for mailer_id in await self.storage.get_mailer_ids():
            data = await self.storage.get_data(mailer_id=mailer_id)
            if data.bot_id not in self._bots:
                logger.error(
                    "Failed to restore mailer for bot id=%d, mailer id=%d.",
                    data.bot_id,
                    mailer_id,
                )
                continue
            unique_mailer_id = await self._ensure_unique_mailer_id(mailer_id=mailer_id)
            mailer = Mailer(
                id=unique_mailer_id,
                settings=data.settings,
                chat_manager=data.chat_manager,
                content=data.content,
                event=self.event,
                language_getter=self.language_getter,
                bot=self._bots[data.bot_id],
                handle_retry_after=self.handle_retry_after,
                kwargs=self.kwargs.copy(),
            )
            self._mailers[unique_mailer_id] = mailer

    async def run_mailers(self) -> None:
        for mailer in self._mailers.values():
            if mailer.status is not MailerStatus.COMPLETED:
                mailer.start()

    def setup(self, dispatcher: Dispatcher, *, include_data: bool = True) -> None:
        dispatcher[self.context_key] = self
        if include_data:
            self.kwargs.update(dispatcher.workflow_data)
        if self.storage:
            dispatcher.startup.register(self.restore_mailers)
        if self.run_on_startup:
            dispatcher.startup.register(self.run_mailers)

    async def _ensure_unique_mailer_id(self, mailer_id: int) -> int:
        if mailer_id not in self._mailers:
            return mailer_id
        new_mailer_id = generate_id(container=self._mailers)
        logger.warning(
            "Duplicate mailer id=%d detected. Generating a new id=%d",
            mailer_id,
            new_mailer_id,
        )
        if self.storage:
            await self.storage.migrate_keys(
                old_mailer_id=mailer_id,
                new_mailer_id=new_mailer_id,
            )
        return new_mailer_id

    def _apply_delete_on_complete(self) -> None:
        async def delete_on_complete(mailer: Mailer, broadcaster: "Broadcaster") -> None:
            await broadcaster.delete_mailer(mailer_id=mailer.id)

        self.event.completed.register(callback=delete_on_complete)
