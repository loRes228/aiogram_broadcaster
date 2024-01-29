from datetime import timedelta
from logging import Logger, getLogger
from typing import Dict, List, Optional, Union

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from redis.asyncio import Redis

from .data import ChatIds, Interval, MailerData, ReplyMarkup
from .mailer import Mailer
from .storage import MailerStorage
from .trigger import TriggerManager


class Broadcaster:
    bot: Bot
    dispatcher: Dispatcher
    storage: MailerStorage
    context_key: str
    logger: Logger
    trigger: TriggerManager
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "bot",
        "dispatcher",
        "storage",
        "context_key",
        "logger",
        "trigger",
        "_mailers",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        redis: Redis,
        *,
        redis_key: str = "BCR",
        context_key: str = "broadcaster",
        logger: Union[Logger, str] = "aiogram.broadcaster",
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.storage = MailerStorage(redis=redis, key_prefix=redis_key)
        self.context_key = context_key
        self.logger = (
            getLogger(name=logger)  # fmt: skip
            if not isinstance(logger, Logger)
            else logger
        )
        self.trigger = TriggerManager(bot=bot, dispatcher=dispatcher)
        self._mailers = {}

    def __getitem__(self, item: int) -> Mailer:
        return self._mailers[item]

    def __len__(self) -> int:
        return len(self._mailers)

    def __repr__(self) -> str:
        return "Broadcaster(total_mailers=%d)" % len(self)

    def __str__(self) -> str:
        return "Broadcaster[%s]" % ", ".join(map(repr, self.mailers()))

    def mailers(self) -> List[Mailer]:
        return list(self._mailers.values())

    def get(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    async def create(
        self,
        chat_ids: ChatIds,
        message: Message,
        interval: Interval,
        *,
        reply_markup: ReplyMarkup = None,
        disable_notification: bool = False,
    ) -> Mailer:
        interval = (
            interval.total_seconds()  # fmt: skip
            if isinstance(interval, timedelta)
            else float(interval)
        )
        data = MailerData.build(
            chat_ids=chat_ids,
            message=message,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
            interval=interval,
        )
        mailer = self._create_mailer(data=data)
        await self.storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    async def startup(self) -> None:
        for mailer_id in await self.storage.get_mailer_ids():
            data = await self.storage.get_data(mailer_id=mailer_id)
            self._create_mailer(data=data, id_=mailer_id)

    def setup(self) -> None:
        self.dispatcher[self.context_key] = self
        self.dispatcher.startup.register(self.startup)

    def _create_mailer(
        self,
        data: MailerData,
        id_: Optional[int] = None,
    ) -> Mailer:
        return Mailer(
            bot=self.bot,
            dispatcher=self.dispatcher,
            logger=self.logger,
            data=data,
            storage=self.storage,
            trigger_manager=self.trigger,
            mailers=self._mailers,
            id_=id_,
        )
