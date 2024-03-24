from typing import Any, Dict, Iterable, Iterator, List, Literal, Optional, Set, Tuple, Union
from uuid import uuid4

from aiogram import Bot, Dispatcher
from pydantic_core import PydanticSerializationError

from .contents import BaseContent
from .default import DefaultMailerProperties
from .event import EventManager
from .l10n import BaseLanguageGetter, L10nContentAdapter
from .logger import logger
from .mailer import Mailer, MailerStatus
from .mailer.chat_engine import ChatEngine, ChatState
from .mailer.multiple import MultipleMailers
from .mailer.settings import MailerSettings
from .placeholder import PlaceholderWizard
from .storage.base import BaseBCRStorage


class Broadcaster:
    _bots: Dict[int, Bot]
    storage: Optional[BaseBCRStorage]
    language_getter: Optional[BaseLanguageGetter]
    default: DefaultMailerProperties
    context_key: str
    kwargs: Dict[str, Any]
    event: EventManager
    placeholder: PlaceholderWizard
    _mailers: Dict[int, Mailer]

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseBCRStorage] = None,
        language_getter: Optional[BaseLanguageGetter] = None,
        default: Optional[DefaultMailerProperties] = None,
        context_key: str = "broadcaster",
        **kwargs: Any,
    ) -> None:
        self._bots = {bot.id: bot for bot in bots}
        self.storage = storage
        self.language_getter = language_getter
        self.default = default or DefaultMailerProperties()
        self.context_key = context_key
        self.kwargs = kwargs
        self.kwargs["broadcaster"] = self

        self.event = EventManager(name="root")
        self.placeholder = PlaceholderWizard(name="root")
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
        handle_retry_after: Optional[bool] = None,
        destroy_on_complete: Optional[bool] = None,
        preserve: Optional[bool] = None,
        disable_events: bool = False,
        exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None,
        **kwargs: Any,
    ) -> MultipleMailers:
        if not bots and not self._bots:
            raise ValueError("At least one bot must be specified.")
        if not bots:
            bots = self.bots
        mailers = [
            await self.create_mailer(
                content=content,
                chats=chats,
                bot=bot,
                interval=interval,
                dynamic_interval=dynamic_interval,
                run_on_startup=run_on_startup,
                handle_retry_after=handle_retry_after,
                destroy_on_complete=destroy_on_complete,
                disable_events=disable_events,
                exclude_placeholders=exclude_placeholders,
                preserve=preserve,
                **kwargs,
            )
            for bot in bots
        ]
        return MultipleMailers(mailers=mailers)

    async def create_mailer(
        self,
        content: BaseContent,
        chats: Iterable[int],
        *,
        bot: Optional[Bot] = None,
        interval: Optional[float] = None,
        dynamic_interval: Optional[bool] = None,
        run_on_startup: Optional[bool] = None,
        handle_retry_after: Optional[bool] = None,
        destroy_on_complete: Optional[bool] = None,
        preserve: Optional[bool] = None,
        disable_events: bool = False,
        exclude_placeholders: Optional[Union[Literal[True], Set[str]]] = None,
        **kwargs: Any,
    ) -> Mailer:
        properties = self.default.prepare(
            interval=interval,
            dynamic_interval=dynamic_interval,
            run_on_startup=run_on_startup,
            handle_retry_after=handle_retry_after,
            destroy_on_complete=destroy_on_complete,
            preserve=preserve,
        )

        if not chats:
            raise ValueError("At least one chat id must be provided.")
        if not bot and not self._bots:
            raise ValueError("At least one bot must be specified.")
        if isinstance(content, L10nContentAdapter) and not self.language_getter:
            raise RuntimeError("To use 'L10nContentAdapter' language_getter must be provided.")
        if properties.preserve and self.storage:
            try:
                content.model_dump_json(exclude_defaults=True)
            except PydanticSerializationError as error:
                raise ValueError("Content cant be serialized to preserving.") from error

        if bot is None:
            bot = self.bots[-1]

        interval = properties.interval
        if properties.dynamic_interval:
            interval = max(0.1, interval / len(set(chats)))

        mailer_id = hash(uuid4())
        settings = MailerSettings(
            interval=interval,
            run_on_startup=properties.run_on_startup,
            disable_events=disable_events,
            handle_retry_after=properties.handle_retry_after,
            destroy_on_complete=properties.destroy_on_complete,
            exclude_placeholders=exclude_placeholders,
            preserved=properties.preserve,
        )
        chat_engine = ChatEngine.from_iterable(
            iterable=chats,
            state=ChatState.PENDING,
            mailer_id=mailer_id,
            storage=self.storage if properties.preserve else None,
        )
        mailer = Mailer(
            id=mailer_id,
            settings=settings,
            chat_engine=chat_engine,
            content=content,
            event=self.event,
            language_getter=self.language_getter,
            placeholder=self.placeholder,
            storage=self.storage if properties.preserve else None,
            mailer_container=self._mailers,
            bot=bot,
            kwargs={**self.kwargs, **kwargs},
        )
        logger.info("Mailer id=%d was created.", mailer_id)
        if not properties.preserve:
            return mailer
        self._mailers[mailer_id] = mailer
        if self.storage:
            await self.storage.set_content(mailer_id=mailer_id, content=content)
            await self.storage.set_chats(mailer_id=mailer_id, chats=chat_engine)
            await self.storage.set_settings(mailer_id=mailer_id, settings=settings)
            await self.storage.set_bot(mailer_id=mailer_id, bot=bot.id)
        return mailer

    async def restore_mailers(self) -> None:
        if not self.storage:
            raise RuntimeError("Storage not specified.")
        for mailer_id in await self.storage.get_mailer_ids():
            bot_id = await self.storage.get_bot(mailer_id=mailer_id)
            if bot_id not in self._bots:
                logger.error(
                    "Failed to restore mailer id=%d, bot with id=%d not specified.",
                    mailer_id,
                    bot_id,
                )
                continue
            content = await self.storage.get_content(mailer_id=mailer_id)
            chat_engine = await self.storage.get_chats(mailer_id=mailer_id)
            settings = await self.storage.get_settings(mailer_id=mailer_id)
            mailer = Mailer(
                id=mailer_id,
                settings=settings,
                chat_engine=chat_engine,
                content=content,
                event=self.event,
                language_getter=self.language_getter,
                placeholder=self.placeholder,
                storage=self.storage,
                mailer_container=self._mailers,
                bot=self._bots[bot_id],
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
