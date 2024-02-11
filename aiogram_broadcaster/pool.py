from random import getrandbits
from typing import Any, Dict, List, Optional

from aiogram import Bot, Dispatcher

from .chat_manager import ChatManager
from .event_manager import EventManager
from .mailer import Mailer
from .messenger import Messenger
from .settings import Settings
from .storage.base import BaseMailerStorage
from .task_manager import TaskManager


class MailerPool:
    bot: Bot
    dispatcher: Dispatcher
    storage: Optional[BaseMailerStorage]
    event_manager: EventManager
    data: Dict[str, Any]
    _mailers: Dict[int, Mailer]

    __slots__ = (
        "_mailers",
        "bot",
        "data",
        "dispatcher",
        "event_manager",
        "storage",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        storage: Optional[BaseMailerStorage],
        event_manager: EventManager,
        **data: Any,
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher
        self.storage = storage
        self.event_manager = event_manager
        self.data = data
        self._mailers = {}

    def __len__(self) -> int:
        return len(self._mailers)

    def get_all(self) -> List[Mailer]:
        return list(self._mailers.values())

    def get(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    async def delete(self, mailer_id: int) -> None:
        if not self.get(mailer_id=mailer_id):
            return
        del self._mailers[mailer_id]
        if self.storage:
            await self.storage.delete_settings(mailer_id=mailer_id)

    async def create(
        self,
        *,
        settings: Settings,
        save_to_storage: bool,
        defined_id: Optional[int] = None,
        **data: Any,
    ) -> Mailer:
        data.update(
            bot=self.bot,
            dispatcher=self.dispatcher,
            **self.data,
            **self.dispatcher.workflow_data,
        )
        mailer_id = defined_id or getrandbits(50)
        task_manager = TaskManager()
        chat_manager = ChatManager(
            mailer_id=mailer_id,
            storage=self.storage,
            settings=settings.chats,
        )
        messenger = Messenger(
            bot=self.bot,
            strategy=settings.mailer.strategy,
            settings=settings.message,
        )
        mailer = Mailer(
            id=mailer_id,
            mailer_pool=self,
            task_manager=task_manager,
            chat_manager=chat_manager,
            event_manager=self.event_manager,
            messenger=messenger,
            settings=settings.mailer,
            data=data,
        )
        self._mailers[mailer_id] = mailer
        if save_to_storage and self.storage:
            await self.storage.set_settings(
                mailer_id=mailer_id,
                settings=settings,
            )
        return mailer

    async def create_all_from_storage(self) -> None:
        if not self.storage:
            return
        for mailer_id in await self.storage.get_mailer_ids():
            settings = await self.storage.get_settings(mailer_id=mailer_id)
            await self.create(
                settings=settings,
                save_to_storage=False,
                defined_id=mailer_id,
            )

    async def run_all(self) -> None:
        for mailer in self.get_all():
            mailer.start()
