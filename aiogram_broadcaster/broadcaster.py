from typing import Any, Dict, Iterable, Literal, Optional, Set, Tuple, Union, cast
from uuid import uuid4

from aiogram import Bot, Dispatcher
from pydantic_core import PydanticSerializationError, ValidationError

from .contents.base import BaseContent, ContentType
from .default import DefaultMailerProperties
from .event import EventManager
from .logger import logger
from .mailer.chat_engine import ChatEngine, ChatState
from .mailer.container import MailerContainer
from .mailer.group import MailerGroup
from .mailer.mailer import Mailer
from .mailer.settings import MailerSettings
from .mailer.status import MailerStatus
from .placeholder import PlaceholderManager
from .storage.base import BaseMailerStorage
from .storage.record import StorageRecord


class Broadcaster(MailerContainer):
    bots: Tuple[Bot, ...]
    storage: Optional[BaseMailerStorage]
    default: DefaultMailerProperties
    context_key: str
    contextual_data: Dict[str, Any]
    event: EventManager
    placeholder: PlaceholderManager

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseMailerStorage] = None,
        default: Optional[DefaultMailerProperties] = None,
        context_key: str = "broadcaster",
        **kwargs: Any,
    ) -> None:
        super().__init__()

        self.bots = bots
        self.storage = storage
        self.default = default or DefaultMailerProperties()
        self.context_key = context_key
        self.contextual_data = kwargs
        self.contextual_data.update(
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
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
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
                data=data,
                **kwargs,
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
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
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
            raise RuntimeError(
                f"Register the {type(content).__name__!r} content "
                f"using the '{type(content).__name__}.register()' method.",
            )

        chats = set(chats)

        if bot is None:
            bot = self.bots[-1]
        if data is None:
            data = {}

        interval = properties.interval
        if properties.dynamic_interval:
            interval = max(0.1, interval / len(chats))

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
        chat_engine = ChatEngine(
            chats={ChatState.PENDING: chats},
            mailer_id=mailer_id,
            storage=self.storage if properties.preserve else None,
        )
        mailer = Mailer(
            id=mailer_id,
            settings=settings,
            chat_engine=chat_engine,
            content=content,
            event=self.event,
            placeholder=self.placeholder,
            storage=self.storage if properties.preserve else None,
            mailer_container=self._mailers,
            bot=bot,
            contextual_data={**self.contextual_data, **data, **kwargs},
        )
        logger.info("Mailer id=%d was created.", mailer_id)
        if not properties.preserve:
            return mailer
        self._mailers[mailer_id] = cast(Mailer, mailer)
        if not self.storage:
            return mailer
        record = StorageRecord(
            content=content,
            chats=chat_engine,
            settings=settings,
            bot=bot.id,
            data=data,
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
            try:
                record = await self.storage.get(mailer_id=mailer_id)
            except ValidationError:
                logger.exception("Failed to restore mailer id=%d.", mailer_id)
                continue
            if record.bot not in bots:
                logger.error(
                    "Failed to restore mailer id=%d, bot with id=%d not defined.",
                    mailer_id,
                    record.bot,
                )
                continue
            mailer = Mailer(
                id=mailer_id,
                settings=record.settings,
                chat_engine=record.chats,
                content=record.content,
                event=self.event,
                placeholder=self.placeholder,
                storage=self.storage,
                mailer_container=self._mailers,
                bot=bots[record.bot],
                contextual_data={**self.contextual_data, **record.data},
            )
            self._mailers[mailer_id] = mailer
            logger.info("Mailer id=%d restored from storage.", mailer_id)

    async def run_startup_mailers(self) -> None:
        for mailer in self.get_mailers(MailerStatus.STOPPED):
            if mailer.settings.run_on_startup:
                mailer.start()

    def setup(self, dispatcher: Dispatcher, *, fetch_workflow_data: bool = True) -> "Broadcaster":
        dispatcher[self.context_key] = self
        self.contextual_data["dispatcher"] = dispatcher
        if fetch_workflow_data:
            self.contextual_data.update(dispatcher.workflow_data)
        if self.storage:
            dispatcher.startup.register(self.storage.startup)
            dispatcher.startup.register(self.restore_mailers)
            dispatcher.shutdown.register(self.storage.shutdown)
        dispatcher.startup.register(self.run_startup_mailers)
        return self
