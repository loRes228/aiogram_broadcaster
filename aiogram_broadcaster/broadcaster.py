from datetime import timedelta
from logging import Logger, getLogger
from typing import Dict, List, Optional, Union

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from .mailer import Mailer
from .models import MailerData
from .storage import Storage
from .types_ import ChatsIds, Interval


DEFAULT_REDIS_KEY = "BCR"
DEFAULT_LOGGER_NAME = "broadcaster"
DEFAULT_CONTEXT_KEY = "broadcaster"


class Broadcaster:
    bot: Bot
    storage: Storage
    logger: Logger
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "bot",
        "storage",
        "logger",
        "_mailers",
    )

    def __init__(
        self,
        bot: Bot,
        redis: Redis,
        *,
        redis_key: str = DEFAULT_REDIS_KEY,
        logger: Union[Logger, str] = DEFAULT_LOGGER_NAME,
    ) -> None:
        if not redis.get_encoder().decode_responses:  # type: ignore[no-untyped-call]
            raise RuntimeError("Redis client must have decode_responses set to True.")
        self.bot = bot
        self.storage = Storage(redis=redis, key_prefix=redis_key)
        if not isinstance(logger, Logger):
            logger = getLogger(name=logger)
        self.logger = logger
        self._mailers = {}

    def setup(
        self,
        dispatcher: Dispatcher,
        context_key: str = DEFAULT_CONTEXT_KEY,
    ) -> None:
        dispatcher[context_key] = self
        dispatcher.startup.register(self.startup)

    async def create(
        self,
        chat_ids: ChatsIds,
        *,
        interval: Interval,
        message_id: int,
        from_chat_id: int,
        notifications: bool = True,
        protect_content: bool = False,
    ) -> Mailer:
        interval = self.validate_interval(interval=interval)
        data = MailerData.build(
            chat_ids=chat_ids,
            interval=interval,
            message_id=message_id,
            from_chat_id=from_chat_id,
            notifications=notifications,
            protect_content=protect_content,
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
            storage=self.storage,
            logger=self.logger,
            mailers=self._mailers,
            id_=id_,
        )

    def validate_interval(self, interval: Interval) -> float:
        if isinstance(interval, timedelta):
            return interval.total_seconds()
        return float(interval)

    def __repr__(self) -> str:
        return f"Broadcaster(total_mailers={len(self.mailers())})"
