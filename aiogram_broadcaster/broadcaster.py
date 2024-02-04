from typing import Any, Iterator, List, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from .data import ChatIdsType, Data, IntervalType, MarkupType
from .event_logs import setup_event_logging
from .event_manager import EventManager
from .mailer import Mailer
from .pool import MailerPool
from .storage.base import BaseMailerStorage, NullMailerStorage


class Broadcaster:
    dispatcher: Dispatcher
    context_key: str
    run_on_startup: bool
    storage: BaseMailerStorage
    event: EventManager
    mailer_pool: MailerPool

    __slots__ = (
        "context_key",
        "dispatcher",
        "event",
        "mailer_pool",
        "run_on_startup",
        "storage",
    )

    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
        storage: Optional[BaseMailerStorage] = None,
        *,
        context_key: str = "broadcaster",
        run_on_startup: bool = False,
        auto_setup: bool = False,
        **kwargs: Any,
    ) -> None:
        self.dispatcher = dispatcher
        self.context_key = context_key
        self.run_on_startup = run_on_startup

        self.storage = storage or NullMailerStorage()
        self.event = EventManager(
            bot=bot,
            dispatcher=dispatcher,
            **dispatcher.workflow_data,
            **kwargs,
        )
        self.mailer_pool = MailerPool(
            bot=bot,
            storage=self.storage,
            event=self.event,
        )

        if auto_setup:
            self.setup()
        setup_event_logging(event=self.event)

    def __repr__(self) -> str:
        return "Broadcaster(total_mailers=%d)" % len(self)

    def __str__(self) -> str:
        return "Broadcaster[%s]" % ", ".join(map(repr, self))

    def __getitem__(self, item: int) -> Mailer:
        if mailer := self.get_mailer(mailer_id=item):
            return mailer
        raise KeyError

    def __contains__(self, item: Mailer) -> bool:
        return item in self.get_mailers()

    def __iter__(self) -> Iterator[Mailer]:
        return iter(self.get_mailers())

    def __len__(self) -> int:
        return len(self.mailer_pool)

    def get_mailers(self) -> List[Mailer]:
        return self.mailer_pool.get_all()

    def get_mailer(self, mailer_id: int) -> Optional[Mailer]:
        return self.mailer_pool.get(id=mailer_id)

    async def create_mailer(
        self,
        chat_ids: ChatIdsType,
        *,
        interval: IntervalType,
        message: Message,
        reply_markup: MarkupType = None,
        disable_notification: bool = False,
        dynamic_interval: bool = True,
        delete_on_complete: bool = False,
        **kwargs: Any,
    ) -> Mailer:
        data = Data.build(
            chat_ids=chat_ids,
            message=message,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
            interval=interval,
            dynamic_interval=dynamic_interval,
            delete_on_complete=delete_on_complete,
        )
        return await self.mailer_pool.create(
            data=data,
            save_to_storage=True,
            **kwargs,
        )

    def setup(self) -> None:
        self.dispatcher[self.context_key] = self
        self.dispatcher.startup.register(self.mailer_pool.create_all_from_storage)
        if self.run_on_startup:
            self.dispatcher.startup.register(self.mailer_pool.run_all)
