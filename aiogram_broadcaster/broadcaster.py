from datetime import timedelta
from typing import Dict, List, Optional, Union

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from .mailer import Mailer
from .models import MailerData
from .storage import Storage


Interval = Union[float, int, timedelta]

DEFAULT_REDIS_KEY = "broadcaster"
DEFAULT_CONTEXT_KEY = "broadcaster"


class Broadcaster:
    bot: Bot
    storage: Storage
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "bot",
        "storage",
        "_mailers",
    )

    def __init__(
        self,
        bot: Bot,
        redis: Redis,
        redis_key: str = DEFAULT_REDIS_KEY,
    ) -> None:
        if not redis.get_encoder().decode_responses:
            raise RuntimeError("Redis client must have decode_responses set to True.")
        self.bot = bot
        self.storage = Storage(redis=redis, key_prefix=redis_key)
        self._mailers = {}

    def setup(
        self,
        dispatcher: Dispatcher,
        context_key: str = DEFAULT_CONTEXT_KEY,
    ) -> None:
        dispatcher.workflow_data.update({context_key: self})
        dispatcher.startup.register(self.startup)

    async def create(
        self,
        *,
        chat_ids: List[int],
        message_id: int,
        from_chat_id: int,
        notifications: bool = True,
        protect_content: bool = False,
        interval: Interval,
    ) -> Mailer:
        overriden_interval = self.validate_interval(interval=interval)
        data = MailerData.build(
            chat_ids=chat_ids,
            interval=overriden_interval,
            message_id=message_id,
            from_chat_id=from_chat_id,
            notifications=notifications,
            protect_content=protect_content,
        )
        mailer = self.create_from_data(data=data)
        await self.storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    def create_from_data(self, *, id_: Optional[int] = None, data: MailerData) -> Mailer:
        mailer = Mailer(id_=id_, bot=self.bot, storage=self.storage, data=data)
        self._mailers[mailer.id] = mailer
        return mailer

    def get(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    async def delete(self, mailer_id: int) -> bool:
        if mailer_id not in self._mailers:
            return False
        self._mailers.pop(mailer_id)
        await self.storage.delete_data(mailer_id=mailer_id)
        return True

    def mailers(self) -> List[Mailer]:
        return list(self._mailers.values())

    async def startup(self) -> None:
        mailers_ids = await self.storage.get_mailer_ids()
        for mailer_id in mailers_ids:
            data = await self.storage.get_data(mailer_id=mailer_id)
            self.create_from_data(id_=mailer_id, data=data)

    def validate_interval(self, interval: Interval) -> float:
        if isinstance(interval, timedelta):
            return interval.total_seconds()
        return float(interval)

    __getitem__ = get
