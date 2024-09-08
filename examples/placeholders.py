import logging
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, Placeholder
from aiogram_broadcaster.contents import TextContent


TOKEN = "123:Abc"
CHATS = {230912392, 122398104, 39431920120}


router = Router(name=__name__)
placeholder = Placeholder(name=__name__)


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster) -> None:
    content = TextContent(text="Hello, $name!")
    mailer = await broadcaster.create_mailer(chats=CHATS, content=content)
    mailer.start()


@placeholder.string(name="name")
async def name_placeholder(chat_id: int, bot: Bot) -> Optional[str]:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    except TelegramAPIError:
        return None
    else:
        return member.user.first_name


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, default=default)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
    broadcaster.setup(dispatcher=dispatcher)
    broadcaster.placeholder.bind(placeholder)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
