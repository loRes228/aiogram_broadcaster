from datetime import timedelta
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from aiogram.types import Message
from redis.asyncio import Redis

from .mailer import Mailer
from .models import MailerData, Statistic
from .storage import Storage
from .types_ import ChatsIds, Interval


if TYPE_CHECKING:
    from asyncio import Task

DEFAULT_REDIS_KEY = "BCR"
DEFAULT_LOGGER_NAME = "broadcaster"
DEFAULT_CONTEXT_KEY = "broadcaster"


class Broadcaster:
    bot: Bot
    dispatcher: Dispatcher
    storage: Storage
    callback_on_failed: Optional[CallableObject]
    logger: Logger
    _mailers: Dict[int, Mailer]
    _callback_tasks: "Set[Task[Any]]"

    __slots__ = (
        "bot",
        "dispatcher",
        "storage",
        "callback_on_failed",
        "logger",
        "_mailers",
        "_callback_tasks",
    )

    def __init__(
        self,
        redis: Redis,
        bot: Bot,
        dispatcher: Dispatcher,
        *,
        callback_on_failed: Optional[CallbackType] = None,
        redis_key: str = DEFAULT_REDIS_KEY,
        logger: Union[Logger, str] = DEFAULT_LOGGER_NAME,
    ) -> None:
        if not redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise RuntimeError("Redis client must have decode_responses set to True.")
        self.bot = bot
        self.dispatcher = dispatcher
        self.storage = Storage(redis=redis, key_prefix=redis_key)
        self.callback_on_failed = (
            CallableObject(callback=callback_on_failed)  # fmt: skip
            if callback_on_failed
            else None
        )
        if not isinstance(logger, Logger):
            logger = getLogger(name=logger)
        self.logger = logger
        self._mailers = {}
        self._callback_tasks = set()

    def setup(self, context_key: str = DEFAULT_CONTEXT_KEY) -> None:
        self.dispatcher[context_key] = self
        self.dispatcher.startup.register(self.startup)

    async def create(
        self,
        chat_ids: ChatsIds,
        message: Message,
        *,
        interval: Interval,
        disable_notification: bool = False,
    ) -> Mailer:
        interval = self.validate_interval(interval=interval)
        data = MailerData.build(
            chat_ids=chat_ids,
            message=message,
            interval=interval,
            disable_notification=disable_notification,
        )
        mailer = self.create_from_data(data=data)
        await self.storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    def get(self, mailer_id: int) -> Mailer:
        return self._mailers[mailer_id]

    async def run(self, mailer_id: int) -> None:
        mailer = self.get(mailer_id=mailer_id)
        await mailer.run()

    def stop(self, mailer_id: int) -> bool:
        mailer = self.get(mailer_id=mailer_id)
        return mailer.stop()

    async def delete(self, mailer_id: int) -> None:
        mailer = self.get(mailer_id=mailer_id)
        await mailer.delete()

    def statistic(self, mailer_id: int) -> Statistic:
        mailer = self.get(mailer_id=mailer_id)
        return mailer.statistic()

    def mailers(self) -> List[Mailer]:
        return list(self._mailers.values())

    async def startup(self) -> None:
        for mailer_id in await self.storage.get_mailer_ids():
            data = await self.storage.get_data(mailer_id=mailer_id)
            self.create_from_data(data=data, id_=mailer_id)

    def create_from_data(
        self,
        data: MailerData,
        id_: Optional[int] = None,
    ) -> Mailer:
        return Mailer(
            data=data,
            bot=self.bot,
            dispatcher=self.dispatcher,
            storage=self.storage,
            logger=self.logger,
            mailers=self._mailers,
            callback_on_failed=self.callback_on_failed,
            callback_tasks=self._callback_tasks,
            id_=id_,
        )

    def validate_interval(self, interval: Interval) -> float:
        if isinstance(interval, timedelta):
            return interval.total_seconds()
        return float(interval)

    def __repr__(self) -> str:
        return f"Broadcaster(total_mailers={len(self.mailers())})"
