from datetime import datetime, timedelta
from typing import Any, List, Optional, Protocol

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from redis.asyncio import Redis

from aiogram_broadcaster import Broadcaster, DefaultMailerProperties
from aiogram_broadcaster.event import EventRouter, skip_event
from aiogram_broadcaster.l10n import BaseLanguageGetter
from aiogram_broadcaster.mailer import Mailer
from aiogram_broadcaster.placeholder import Placeholder
from aiogram_broadcaster.storage.redis import RedisBCRStorage


event = EventRouter(name=__name__)
placeholder = Placeholder(name=__name__)


class Database(Protocol):
    async def get_active_user_ids(self) -> List[int]: ...

    async def set_user_activity(self, user_id: int, *, active: bool) -> None: ...

    async def get_user_language(self, user_id: int) -> str: ...

    async def get_user_nickname(self, user_id: int) -> str: ...


class LanguageGetter(BaseLanguageGetter):
    async def __call__(self, chat_id: int, database: Database) -> Optional[str]:
        return await database.get_user_language(user_id=chat_id)


@event.completed()
async def append_new_chats(mailer: Mailer, database: Database) -> None:
    chats = await database.get_active_user_ids()
    if not await mailer.add_chats(chats=chats):
        return
    await mailer.run()
    skip_event()


@event.completed()
async def notify_complete(mailer: Mailer, bot: Bot, publisher_id: int, **kwargs: Any) -> None:
    text = (
        f"Broadcasting has been completed!\n"
        f"Mailer ID: {mailer.id} | Bot ID: {bot.id}\n"
        f"{mailer}"
    )
    await bot.send_message(
        chat_id=publisher_id,
        text=text,
        reply_to_message_id=kwargs.get("message_id"),
    )


@event.failed_sent()
async def on_bot_blocked(chat_id: int, error: Exception, database: Database) -> None:
    if not isinstance(error, TelegramBadRequest):
        return
    await database.set_user_activity(user_id=chat_id, active=False)


@placeholder(key="name")
async def name_getter(chat_id: int, bot: Bot) -> str:
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


@placeholder(key="username")
async def username_getter(chat_id: int, bot: Bot) -> str:
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.username or member.user.first_name


@placeholder(key="nickname")
async def nickname_getter(chat_id: int, database: Database) -> str:
    return await database.get_user_nickname(user_id=chat_id)


@placeholder(key="date")
async def date_getter() -> str:
    return datetime.now().strftime("%F %T")  # noqa: DTZ005


def setup_broadcaster(*bots: Bot, dispatcher: Dispatcher, redis: Redis) -> None:
    storage = RedisBCRStorage(redis=redis)
    language_getter = LanguageGetter()
    default = DefaultMailerProperties(
        interval=timedelta(hours=12).total_seconds(),
        dynamic_interval=True,
        run_on_startup=True,
        handle_retry_after=True,
        destroy_on_complete=True,
        preserve=True,
    )
    broadcaster = Broadcaster(
        *bots,
        storage=storage,
        language_getter=language_getter,
        default=default,
    )
    broadcaster.event.include(event)
    broadcaster.placeholder.include(placeholder)
    broadcaster.setup(dispatcher=dispatcher, include_data=True)
