import logging
import sys
from secrets import choice
from typing import Any, List

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from pydantic import SerializeAsAny

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import BaseContent, LazyContent, TextContent


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


class RandomizedContent(LazyContent):
    contents: List[SerializeAsAny[BaseContent]]

    async def __call__(self) -> BaseContent:
        return choice(self.contents)


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    content = RandomizedContent(
        contents=[
            TextContent(text="Hello!"),
            TextContent(text="Hi!"),
        ],
    )
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
