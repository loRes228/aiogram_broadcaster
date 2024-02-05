from typing import Any, Dict, List, Optional

from aiogram import Bot

from aiogram_broadcaster.data import Data
from aiogram_broadcaster.event_manager import EventManager
from aiogram_broadcaster.storage.base import BaseMailerStorage

from .mailer import Mailer


class MailerPool:
    bot: Bot
    storage: BaseMailerStorage
    event: EventManager
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "_mailers",
        "bot",
        "event",
        "storage",
    )

    def __init__(
        self,
        *,
        bot: Bot,
        storage: BaseMailerStorage,
        event: EventManager,
    ) -> None:
        self.bot = bot
        self.storage = storage
        self.event = event
        self._mailers = {}

    def __len__(self) -> int:
        return len(self._mailers)

    def get_all(self) -> List[Mailer]:
        return list(self._mailers.values())

    def get(self, id: int) -> Optional[Mailer]:  # noqa: A002
        return self._mailers.get(id)

    async def delete(self, id: int) -> None:  # noqa: A002
        del self._mailers[id]
        await self.storage.delete_data(mailer_id=id)

    async def create(
        self,
        *,
        data: Data,
        save_to_storage: bool,
        id: Optional[int] = None,  # noqa: A002
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Mailer:
        mailer = Mailer(
            bot=self.bot,
            data=data,
            storage=self.storage,
            event=self.event,
            pool=self,
            id_=id,
            kwargs=kwargs or {},
        )
        self._mailers[mailer.id] = mailer
        if save_to_storage:
            await self.storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    async def create_all_from_storage(self) -> None:
        for mailer_id in await self.storage.get_mailer_ids():
            data = await self.storage.get_data(mailer_id=mailer_id)
            await self.create(
                data=data,
                save_to_storage=False,
                id=mailer_id,
            )

    async def run_all(self) -> None:
        for mailer in self.get_all():
            mailer.start()
