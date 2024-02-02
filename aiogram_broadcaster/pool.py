from logging import Logger
from typing import Dict, List, Optional

from aiogram import Bot

from .data import Data
from .event import EventManager
from .mailer import Mailer
from .storage.base import BaseMailerStorage


class MailerPool:
    bot: Bot
    storage: BaseMailerStorage
    event: EventManager
    logger: Logger
    mailers: Dict[int, Mailer]

    __slots__ = (
        "bot",
        "event",
        "logger",
        "mailers",
        "storage",
    )

    def __init__(
        self,
        bot: Bot,
        storage: BaseMailerStorage,
        event: EventManager,
    ) -> None:
        self.bot = bot
        self.storage = storage
        self.event = event
        self.mailers = {}

    def __len__(self) -> int:
        return len(self.mailers)

    def get_all(self) -> List[Mailer]:
        return list(self.mailers.values())

    def get(self, id: int) -> Optional[Mailer]:  # noqa: A002
        return self.mailers.get(id)

    async def delete(self, id: int) -> None:  # noqa: A002
        del self.mailers[id]
        await self.storage.delete_data(mailer_id=id)

    async def create(
        self,
        *,
        data: Data,
        delete_on_complete: bool,
        save_to_storage: bool,
        id: Optional[int] = None,  # noqa: A002
    ) -> Mailer:
        mailer = Mailer(
            bot=self.bot,
            data=data,
            storage=self.storage,
            event=self.event,
            pool=self,
            delete_on_complete=delete_on_complete,
            id_=id,
        )
        self.mailers[mailer.id] = mailer
        if save_to_storage:
            await self.storage.set_data(mailer_id=mailer.id, data=data)
        return mailer

    async def create_all_from_storage(self) -> None:
        for mailer_id in await self.storage.get_mailer_ids():
            data = await self.storage.get_data(mailer_id=mailer_id)
            await self.create(
                data=data,
                delete_on_complete=False,
                save_to_storage=False,
                id=mailer_id,
            )
