import logging
import sys
from datetime import datetime, tzinfo
from typing import Any, Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, PlaceholderItem, PlaceholderRouter
from aiogram_broadcaster.contents import TextContent


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)
placeholder = PlaceholderRouter(name=__name__)


@placeholder(key="mention")
async def mention_placeholder(chat_id: int, bot: Bot) -> str:
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.mention_html(name=member.user.first_name)


class TimePlaceholder(PlaceholderItem, key="time"):
    tz: Optional[tzinfo]
    fmt: str

    def __init__(
        self,
        tz: Optional[tzinfo] = None,
        fmt: str = "%T",
    ) -> None:
        self.tz = tz
        self.fmt = fmt

    async def __call__(self) -> str:
        return datetime.now(self.tz).time().strftime(self.fmt)


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    content = TextContent(text="Hello, $mention! Current time: $time")
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        bot=bot,
        interval=1,
    )
    mailer.start()
    await message.reply(text="Run broadcasting...")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, default=default)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster()
    broadcaster.placeholder.include(placeholder)
    broadcaster.placeholder.register(TimePlaceholder())
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
