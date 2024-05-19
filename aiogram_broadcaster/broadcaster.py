from typing import Any, Dict, Iterable, Literal, Optional, Set, Tuple, Union, cast
from uuid import uuid4

from aiogram import Bot, Dispatcher
from pydantic import JsonValue
from pydantic_core import PydanticSerializationError, ValidationError

from . import loggers
from .contents.base import BaseContent, ContentType
from .event import EventManager
from .mailer.chat_engine import ChatsRegistry
from .mailer.container import MailerContainer
from .mailer.group import MailerGroup
from .mailer.mailer import Mailer
from .mailer.settings import DefaultMailerSettings, MailerSettings
from .mailer.status import MailerStatus
from .placeholder import PlaceholderManager
from .storage.base import BaseMailerStorage, StorageRecord


class Broadcaster(MailerContainer):
    bots: Tuple[Bot, ...]
    storage: Optional[BaseMailerStorage]
    default: DefaultMailerSettings
    context_key: str
    context: Dict[str, Any]
    event: EventManager
    placeholder: PlaceholderManager

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseMailerStorage] = None,
        default: Optional[DefaultMailerSettings] = None,
        context_key: str = "broadcaster",
        **context: Any,
    ) -> None:
        super().__init__()

        self.bots = bots
        self.storage = storage
        self.default = default or DefaultMailerSettings()
        self.context_key = context_key
        self.context = context
        self.context.update(
            {self.context_key: self},
            bots=self.bots,
        )

        self.event = EventManager(name="root")
        self.placeholder = PlaceholderManager(name="root")

    def as_group(self) -> MailerGroup:
        if not self._mailers:
            raise RuntimeError("No mailers for grouping.")
        return MailerGroup(*self._mailers.values())

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
        stored_context: Optional[Dict[str, JsonValue]] = None,
        **context: Any,
    ) -> MailerGroup:
        if not bots and not self.bots:
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
                preserve=preserve,
                disable_events=disable_events,
                exclude_placeholders=exclude_placeholders,
                stored_context=stored_context,
                **context,
            )
            for bot in bots
        ]
        return MailerGroup(*mailers)

    async def create_mailer(
        self,
        content: ContentType,
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
        stored_context: Optional[Dict[str, JsonValue]] = None,
        **context: Any,
    ) -> Mailer[ContentType]:
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
        if not bot and not self.bots:
            raise ValueError("At least one bot must be specified.")
        if not content.is_registered():
            raise ValueError(
                f"Register the {type(content).__name__!r} content "
                f"using the '{type(content).__name__}.register()' method.",
            )
        chats = set(chats)
        if bot is None:
            bot = self.bots[-1]
        if properties.dynamic_interval:
            properties.interval = max(0.1, properties.interval / len(chats))
        if stored_context is None:
            stored_context = {}
        mailer_id = hash(uuid4())
        settings = MailerSettings(
            interval=properties.interval,
            run_on_startup=properties.run_on_startup,
            handle_retry_after=properties.handle_retry_after,
            destroy_on_complete=properties.destroy_on_complete,
            disable_events=disable_events,
            exclude_placeholders=exclude_placeholders,
            preserved=properties.preserve,
        )
        chats_registry = ChatsRegistry.from_iterable(chats=chats)
        mailer = Mailer(
            id=mailer_id,
            settings=settings,
            chats=chats_registry,
            content=content,
            event=self.event,
            placeholder=self.placeholder,
            storage=self.storage if properties.preserve else None,
            mailer_container=self._mailers,
            bot=bot,
            context={**self.context, **stored_context, **context},
        )
        loggers.pool.info("Mailer id=%d was created.", mailer_id)
        if not properties.preserve:
            return mailer
        self._mailers[mailer_id] = cast(Mailer, mailer)
        if not self.storage:
            return mailer
        record = StorageRecord(
            content=content,
            chats=chats_registry,
            settings=settings,
            bot_id=bot.id,
            context=stored_context,
        )
        try:
            record.model_dump_json(exclude_defaults=True)
        except PydanticSerializationError as error:
            del self._mailers[mailer_id]
            raise RuntimeError("Record cant be serialized to preserving.") from error
        await self.storage.set(mailer_id=mailer_id, record=record)
        return mailer

    async def restore_mailers(self) -> None:
        if not self.storage:
            raise RuntimeError("Storage not found.")
        mailer_ids = await self.storage.get_mailer_ids()
        if not mailer_ids:
            return
        bots = {bot.id: bot for bot in self.bots}
        for mailer_id in mailer_ids:
            if mailer_id in self._mailers:
                continue
            try:
                record = await self.storage.get(mailer_id=mailer_id)
            except ValidationError:
                loggers.pool.exception("Failed to restore mailer id=%d.", mailer_id)
                continue
            if record.bot_id not in bots:
                loggers.pool.error(
                    "Failed to restore mailer id=%d, bot with id=%d not defined.",
                    mailer_id,
                    record.bot_id,
                )
                continue
            mailer = Mailer(
                id=mailer_id,
                settings=record.settings,
                chats=record.chats,
                content=record.content,
                event=self.event,
                placeholder=self.placeholder,
                storage=self.storage,
                mailer_container=self._mailers,
                bot=bots[record.bot_id],
                context={**self.context, **record.context},
            )
            self._mailers[mailer_id] = mailer
            loggers.pool.info("Mailer id=%d restored from storage.", mailer_id)

    async def run_startup_mailers(self) -> None:
        for mailer in self.get_mailers(MailerStatus.STOPPED):
            if mailer.settings.run_on_startup:
                mailer.start()

    def setup(
        self,
        dispatcher: Dispatcher,
        *,
        fetch_dispatcher_context: bool = True,
        restore_mailers: bool = True,
        run_mailers: bool = True,
    ) -> "Broadcaster":
        dispatcher[self.context_key] = self
        self.context["dispatcher"] = dispatcher
        if fetch_dispatcher_context:
            self.context.update(dispatcher.workflow_data)
        if self.storage:
            dispatcher.startup.register(self.storage.startup)
            dispatcher.shutdown.register(self.storage.shutdown)
            if restore_mailers:
                dispatcher.startup.register(self.restore_mailers)
        if run_mailers:
            dispatcher.startup.register(self.run_startup_mailers)
        return self
