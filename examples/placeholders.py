import logging
import sys
from datetime import datetime, timezone, tzinfo
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import BasePlaceholder, Broadcaster, Placeholder
from aiogram_broadcaster.contents import TextContent


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)
placeholder = Placeholder(name=__name__)


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster) -> Any:
    content = TextContent(text="Hello, $name!")
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
    )
    mailer.start()
    await message.answer(text="Run broadcasting...")


@placeholder(key="name")
async def get_username(chat_id: int, bot: Bot) -> str:
    """Retrieves the username using the Telegram Bot API."""
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


class DatePlaceholder(BasePlaceholder, key="date"):
    def __init__(
        self,
        tz: tzinfo = timezone.utc,
        fmt: str = "%F %T",
    ) -> None:
        self.tz = tz
        self.fmt = fmt

    async def __call__(self) -> str:
        return datetime.now(self.tz).strftime(self.fmt)


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
    broadcaster.placeholder.include(placeholder)
    broadcaster.placeholder.register(DatePlaceholder())
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
