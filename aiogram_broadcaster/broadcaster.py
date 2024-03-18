from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)
from uuid import uuid4

from aiogram import Bot, Dispatcher
from pydantic_core import PydanticSerializationError

from .contents import BaseContent
from .event import EventRouter, RootEventRouter
from .l10n import BaseLanguageGetter, L10nContentAdapter
from .logger import logger
from .mailer import Mailer, MailerStatus
from .mailer.chat_manager import ChatManager, ChatState
from .mailer.multiple import MultipleMailers
from .mailer.settings import MailerSettings
from .placeholder import PlaceholderWizard
from .storage.base import BaseBCRStorage, DataComposer


class Broadcaster:
    _bots: Dict[int, Bot]
    storage: Optional[BaseBCRStorage]
    language_getter: Optional[BaseLanguageGetter]
    context_key: str
    interval: float
    dynamic_interval: bool
    run_on_startup: bool
    disable_events: bool
    handle_retry_after: bool
    destroy_on_complete: bool
    preserve_mailers: bool
    kwargs: Dict[str, Any]
    placeholder_wizard: PlaceholderWizard
    event: EventRouter
    _mailers: Dict[int, Mailer]

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseBCRStorage] = None,
        language_getter: Optional[BaseLanguageGetter] = None,
        placeholders: Optional[Mapping[str, Any]] = None,
        context_key: str = "broadcaster",
        interval: float = 1,
        dynamic_interval: bool = False,
        run_on_startup: bool = False,
        disable_events: bool = False,
        handle_retry_after: bool = False,
        destroy_on_complete: bool = False,
        preserve_mailers: bool = True,
        **kwargs: Any,
    ) -> None:
        self._bots = {bot.id: bot for bot in bots}
        self.storage = storage
        self.language_getter = language_getter
        self.interval = interval
        self.dynamic_interval = dynamic_interval
        self.run_on_startup = run_on_startup
        self.disable_events = disable_events
        self.handle_retry_after = handle_retry_after
        self.destroy_on_complete = destroy_on_complete
        self.preserve_mailers = preserve_mailers
        self.context_key = context_key
        self.kwargs = kwargs
        self.kwargs["broadcaster"] = self

        self.placeholder_wizard = PlaceholderWizard(
            placeholders={} if placeholders is None else placeholders,
        )
        self.event = RootEventRouter(name="root")
        self._mailers = {}

    def __repr__(self) -> str:
        return f"Broadcaster(total_mailers={len(self)})"

    def __str__(self) -> str:
        return f"Broadcaster[{', '.join(map(repr, self))}]"

    def __contains__(self, item: int) -> bool:
        return item in self._mailers

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
    def mailers(self) -> Dict[int, Mailer]:
        return self._mailers

    def get_mailers(self) -> List[Mailer]:
        return list(self._mailers.values())

    def get_mailer(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    def include_event(self, event: EventRouter) -> EventRouter:
        return self.event.include_event(event=event)

    def include_events(self, *events: EventRouter) -> None:
        self.event.include_events(*events)

    def as_multiple(self) -> MultipleMailers:
        return MultipleMailers(mailers=self._mailers.values())

    async def create_mailers(
        self,
        *bots: Bot,
        content: BaseContent,
        chats: Iterable[int],
        interval: Optional[float] = None,
        dynamic_interval: Optional[bool] = None,
        run_on_startup: Optional[bool] = None,
        disable_events: Optional[bool] = None,
        handle_retry_after: Optional[bool] = None,
        destroy_on_complete: Optional[bool] = None,
        exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None,
        preserve: Optional[bool] = None,
        **kwargs: Any,
    ) -> MultipleMailers:
        if not bots:
            raise ValueError("At least one bot must be provided.")
        mailers = [
            await self.create_mailer(
                content=content,
                chats=chats,
                bot=bot,
                interval=interval,
                dynamic_interval=dynamic_interval,
                run_on_startup=run_on_startup,
                disable_events=disable_events,
                handle_retry_after=handle_retry_after,
                destroy_on_complete=destroy_on_complete,
                exclude_placeholders=exclude_placeholders,
                preserve=preserve,
                **kwargs,
            )
            for bot in bots
        ]
        return MultipleMailers(mailers=mailers)

    async def create_mailer(  # noqa: C901, C901, PLR0912
        self,
        content: BaseContent,
        chats: Iterable[int],
        *,
        bot: Optional[Bot] = None,
        interval: Optional[float] = None,
        dynamic_interval: Optional[bool] = None,
        run_on_startup: Optional[bool] = None,
        disable_events: Optional[bool] = None,
        handle_retry_after: Optional[bool] = None,
        destroy_on_complete: Optional[bool] = None,
        exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None,
        preserve: Optional[bool] = None,
        **kwargs: Any,
    ) -> Mailer:
        if not chats:
            raise ValueError("At least one chat id must be provided.")

        if not bot and not self._bots:
            raise ValueError("At least one bot must be specified.")

        if isinstance(content, L10nContentAdapter) and not self.language_getter:
            raise RuntimeError("To use 'L10nContentAdapter' language_getter must be provided.")

        if not bot:
            bot = self.bots[-1]

        if interval is None:
            interval = self.interval
        if dynamic_interval is None:
            dynamic_interval = self.dynamic_interval
        if run_on_startup is None:
            run_on_startup = self.run_on_startup
        if disable_events is None:
            disable_events = self.disable_events
        if handle_retry_after is None:
            handle_retry_after = self.handle_retry_after
        if destroy_on_complete is None:
            destroy_on_complete = self.destroy_on_complete
        if preserve is None:
            preserve = self.preserve_mailers

        if preserve and self.storage:
            try:
                content.model_dump_json(exclude_defaults=True)
            except PydanticSerializationError as error:
                raise ValueError("Content cant be serialized to preserving.") from error

        if dynamic_interval:
            interval = interval / len(set(chats))

        mailer_id = hash(uuid4())
        settings = MailerSettings(
            interval=interval,
            run_on_startup=run_on_startup,
            disable_events=disable_events,
            handle_retry_after=handle_retry_after,
            destroy_on_complete=destroy_on_complete,
            exclude_placeholders=exclude_placeholders,
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
            placeholder_wizard=self.placeholder_wizard,
            storage=self.storage if preserve else None,
            mailer_container=self._mailers,
            bot=bot,
            kwargs={**self.kwargs, **kwargs},
        )
        logger.info("Mailer id=%d was created.", mailer_id)
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
                    "Failed to restore mailer id=%d, bot with id=%d not specified.",
                    mailer_id,
                    data.bot_id,
                )
                continue
            mailer = Mailer(
                id=mailer_id,
                settings=data.settings,
                chat_manager=data.chat_manager,
                content=data.content,
                event=self.event,
                language_getter=self.language_getter,
                placeholder_wizard=self.placeholder_wizard,
                storage=self.storage,
                mailer_container=self._mailers,
                bot=self._bots[data.bot_id],
                kwargs=self.kwargs.copy(),
            )
            self._mailers[mailer_id] = mailer
            logger.info("Mailer id=%d restored from storage.", mailer_id)

    async def run_mailers(self) -> None:
        for mailer in self._mailers.values():
            if not mailer.settings.run_on_startup:
                continue
            if mailer.status is not MailerStatus.STOPPED:
                continue
            mailer.start()

    def setup(self, dispatcher: Dispatcher, *, include_data: bool = True) -> None:
        dispatcher[self.context_key] = self
        if include_data:
            self.kwargs.update(dispatcher.workflow_data)
        if self.storage:
            dispatcher.startup.register(self.restore_mailers)
        dispatcher.startup.register(self.run_mailers)
