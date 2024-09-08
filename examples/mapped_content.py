import logging
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import TextContent
from aiogram_broadcaster.contents.adapters import MappedContentAdapter


TOKEN = "123:Abc"
CHATS = {230912392, 122398104, 39431920120}


router = Router(name=__name__)


class LanguageContentAdapter(MappedContentAdapter):
    async def __call__(self, chat_id: int, bot: Bot) -> Optional[str]:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
        except TelegramAPIError:
            return None
        else:
            return member.user.language_code


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster) -> None:
    content = LanguageContentAdapter(
        default=TextContent(text="Hello!"),
        uk=TextContent(text="Привіт!"),
        ru=TextContent(text="Привет!"),
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
