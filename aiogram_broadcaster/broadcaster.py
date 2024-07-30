from collections.abc import Iterable
from typing import Any, Optional

from aiogram import Bot, Dispatcher, F
from magic_filter import MagicFilter
from pydantic import JsonValue
from typing_extensions import Self

from aiogram_broadcaster.utils.logger import logger

from .contents.base import ContentType
from .event.manager import EventManager
from .intervals.base import BaseInterval
from .mailer.container import MailerContainer
from .mailer.group import MailerGroup
from .mailer.mailer import Mailer
from .mailer.status import MailerStatus
from .placeholder.manager import PlaceholderManager
from .storages.base import BaseStorage


class Broadcaster(MailerContainer):
    bots: tuple[Bot, ...]
    storage: Optional[BaseStorage]
    context: dict[str, Any]
    event: EventManager
    placeholder: PlaceholderManager

    def __init__(
        self,
        *bots: Bot,
        storage: Optional[BaseStorage] = None,
        **context: Any,
    ) -> None:
        super().__init__()

        self.bots = bots
        self.storage = storage
        self.context = context
        self.context["bots"] = self.bots

        self.event = EventManager(name="root")
        self.placeholder = PlaceholderManager(name="root")

    def get_mailers(self, magic: Optional[MagicFilter] = None) -> MailerGroup:
        mailers = list(filter(magic.resolve, self)) if magic else list(self)
        return MailerGroup(*mailers)

    async def create_mailers(
        self,
        *bots: Bot,
        chats: Iterable[int],
        content: ContentType,
        interval: Optional[BaseInterval] = None,
        **context: JsonValue,
    ) -> MailerGroup[ContentType]:
        if not bots and not self.bots:
            raise ValueError("At least one bot must be provided.")
        bots = bots or self.bots
        mailers = [
            await self.create_mailer(
                chats=chats,
                content=content,
                bot=bot,
                interval=interval,
                **context,
            )
            for bot in bots
        ]
        return MailerGroup(*mailers)

    async def create_mailer(
        self,
        chats: Iterable[int],
        content: ContentType,
        bot: Optional[Bot] = None,
        interval: Optional[BaseInterval] = None,
        **context: JsonValue,
    ) -> Mailer[ContentType]:
        return await Mailer.create(
            broadcaster=self,
            chats=chats,
            content=content,
            bot=bot,
            interval=interval,
            **context,
        )

    async def restore_mailers(self) -> None:
        if not self.storage:
            raise ValueError("Storage not found.")
        async for mailer_id, record in self.storage.get_records():
            try:
                await Mailer.create_from_record(
                    broadcaster=self,
                    mailer_id=mailer_id,
                    record=record,
                )
            except Exception:
                logger.exception("Failed to restore mailer id=%d.", mailer_id)

    async def run_mailers(self) -> None:
        self.get_mailers(magic=F.status.is_(MailerStatus.STOPPED)).start()

    def setup(self, dispatcher: Dispatcher, *, context_key: str = "broadcaster") -> Self:
        self.context[context_key] = self
        self.context.update(dispatcher.workflow_data, dispatcher=dispatcher)
        dispatcher[context_key] = self
        if self.storage:
            dispatcher.startup.register(self.storage.startup)
            dispatcher.shutdown.register(self.storage.shutdown)
            dispatcher.startup.register(self.restore_mailers)
        dispatcher.startup.register(self.run_mailers)
        return self
