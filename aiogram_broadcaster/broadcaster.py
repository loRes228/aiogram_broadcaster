from logging import Logger
from typing import List, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from .data import ChatIds, Data, Interval, ReplyMarkup
from .event import EventManager
from .event_logs import setup_event_logging
from .mailer import Mailer
from .pool import MailerPool
from .storage.base import BaseStorage, NullStorage


class Broadcaster:
    bot: Bot
    dispatcher: Dispatcher
    context_key: str
    storage: BaseStorage
    logger: Logger
    event: EventManager
    pool: MailerPool

    __slots__ = (
        "bot",
        "context_key",
        "dispatcher",
        "event",
        "logger",
        "pool",
        "storage",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        storage: Optional[BaseStorage] = None,
        *,
        context_key: str = "broadcaster",
        event_logging: bool = True,
        setup: bool = True,
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.context_key = context_key
        self.storage = storage or NullStorage()
        self.event = EventManager(bot=bot, dispatcher=dispatcher)
        self.pool = MailerPool(
            bot=bot,
            storage=self.storage,
            event=self.event,
        )
        if event_logging:
            setup_event_logging(event=self.event)
        if setup:
            self._setup()

    def __getitem__(self, item: int) -> Mailer:
        if mailer := self.get(mailer_id=item):
            return mailer
        raise KeyError

    def __len__(self) -> int:
        return len(self.pool)

    def __repr__(self) -> str:
        return "Broadcaster(total_mailers=%d)" % len(self)

    def __str__(self) -> str:
        return "Broadcaster[%s]" % ", ".join(map(repr, self.mailers()))

    def mailers(self) -> List[Mailer]:
        return self.pool.get_all()

    def get(self, mailer_id: int) -> Optional[Mailer]:
        return self.pool.get(id=mailer_id)

    async def create(
        self,
        chat_ids: ChatIds,
        *,
        interval: Interval,
        message: Message,
        reply_markup: ReplyMarkup = None,
        disable_notification: bool = False,
        dynamic_interval: bool = True,
        delete_on_complete: bool = False,
    ) -> Mailer:
        data = Data.build(
            chat_ids=chat_ids,
            message=message,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
            interval=interval,
            dynamic_interval=dynamic_interval,
        )
        return await self.pool.create(
            data=data,
            delete_on_complete=delete_on_complete,
        )

    def _setup(self) -> None:
        self.dispatcher[self.context_key] = self
        self.dispatcher.startup.register(self.pool.create_all_from_storage)
