from datetime import timedelta
from logging import Logger, getLogger
from typing import Dict, List, Optional, Union

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from .data import ChatIds, Interval, MailerData, ReplyMarkup
from .mailer import Mailer
from .storage.base import BaseStorage, NullStorage
from .trigger import TriggerManager


class Broadcaster:
    bot: Bot
    dispatcher: Dispatcher
    storage: BaseStorage
    context_key: str
    logger: Logger
    trigger: TriggerManager
    _null_storage: NullStorage
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "bot",
        "dispatcher",
        "storage",
        "context_key",
        "logger",
        "trigger",
        "_null_storage",
        "_mailers",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        storage: Optional[BaseStorage] = None,
        *,
        logger: Union[Logger, str] = "aiogram.broadcaster",
        context_key: str = "broadcaster",
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self._null_storage = NullStorage()
        self.storage = storage or self._null_storage
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
        *,
        message: Message,
        reply_markup: ReplyMarkup = None,
        disable_notification: bool = False,
        interval: Interval,
        dynamic_interval: bool = False,
        preserve: bool = True,
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
            dynamic_interval=dynamic_interval,
        )
        storage = self.storage if preserve else self._null_storage
        mailer = self._create_mailer(data=data, storage=storage)
        await storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    async def startup(self) -> None:
        mailer_ids = await self.storage.get_mailer_ids()
        if not mailer_ids:
            return
        for mailer_id in mailer_ids:
            data = await self.storage.get_data(mailer_id=mailer_id)
            self._create_mailer(data=data, storage=self.storage, id_=mailer_id)

    def setup(self) -> None:
        self.dispatcher[self.context_key] = self
        self.dispatcher.startup.register(self.startup)

    def _create_mailer(
        self,
        *,
        data: MailerData,
        storage: BaseStorage,
        id_: Optional[int] = None,
    ) -> Mailer:
        return Mailer(
            bot=self.bot,
            logger=self.logger,
            data=data,
            storage=storage,
            trigger_manager=self.trigger,
            mailers=self._mailers,
            id_=id_,
        )
