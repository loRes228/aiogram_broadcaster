# ruff: noqa: PLR2004, DTZ005

import logging
import sys
from datetime import datetime
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import LazyContent, TextContent


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


class TimeSensitiveContent(LazyContent):
    async def __call__(self) -> TextContent:
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return TextContent(text="Good morning!")
        if 12 <= hour < 18:
            return TextContent(text="Good afternoon!")
        if 18 <= hour < 24:
            return TextContent(text="Good evening!")
        return TextContent(text="Good night!")


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    content = TimeSensitiveContent()
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        bot=bot,
        interval=1,
    )
    mailer.start()
    await message.answer(text="Run broadcasting...")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster()
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
