import logging
import sys
from secrets import choice

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from pydantic import SerializeAsAny

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import BaseContent, TextContent
from aiogram_broadcaster.contents.adapters import LazyContentAdapter


TOKEN = "123:Abc"
CHATS = {230912392, 122398104, 39431920120}


router = Router(name=__name__)


class RandomizedContentAdapter(LazyContentAdapter):
    contents: list[SerializeAsAny[BaseContent]]

    async def __call__(self) -> BaseContent:
        return choice(self.contents)


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster) -> None:
    content = RandomizedContentAdapter(
        contents=[
            TextContent(text="Hi there!"),
            TextContent(text="Greetings!"),
            TextContent(text="Hey! How's it going?"),
        ],
    )
    mailer = await broadcaster.create_mailer(chats=CHATS, content=content)
    mailer.start()


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, default=default)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
