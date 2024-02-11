from typing import Any, Dict, Iterator, List, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from .enums import Strategy
from .event_manager import EventManager
from .mailer import Mailer
from .pool import MailerPool
from .settings import ChatIdsType, IntervalType, ReplyMarkupType, Settings
from .storage.base import BaseMailerStorage


class Broadcaster:
    dispatcher: Dispatcher
    context_key: str
    run_on_startup: bool
    event: EventManager
    mailer_pool: MailerPool
    data: Dict[str, Any]

    __slots__ = (
        "context_key",
        "data",
        "dispatcher",
        "event",
        "mailer_pool",
        "run_on_startup",
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
        **data: Any,
    ) -> None:
        self.dispatcher = dispatcher
        self.context_key = context_key
        self.run_on_startup = run_on_startup

        self.event = EventManager()
        self.mailer_pool = MailerPool(
            bot=bot,
            dispatcher=dispatcher,
            storage=storage,
            event_manager=self.event,
            **data,
        )

        if auto_setup:
            self.setup()

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
        return self.mailer_pool.get(mailer_id=mailer_id)

    async def create_mailer(
        self,
        chat_ids: ChatIdsType,
        message: Message,
        *,
        reply_markup: ReplyMarkupType = None,
        disable_notification: bool = False,
        protect_content: bool = False,
        strategy: Strategy = Strategy.SEND,
        interval: IntervalType = 1,
        dynamic_interval: bool = False,
        disable_events: bool = False,
        delete_on_complete: bool = False,
        **data: Any,
    ) -> Mailer:
        settings = Settings.build(
            chat_ids=chat_ids,
            message=message,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
            protect_content=protect_content,
            strategy=strategy,
            interval=interval,
            dynamic_interval=dynamic_interval,
            disable_events=disable_events,
            delete_on_complete=delete_on_complete,
        )
        return await self.mailer_pool.create(
            settings=settings,
            save_to_storage=True,
            **data,
        )

    def setup(self) -> None:
        self.dispatcher[self.context_key] = self
        self.dispatcher.startup.register(self.mailer_pool.create_all_from_storage)
        if self.run_on_startup:
            self.dispatcher.startup.register(self.mailer_pool.run_all)
