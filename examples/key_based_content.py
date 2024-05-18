import logging
import sys
from typing import Any, Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import KeyBasedContent, TextContent


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


class LanguageBasedContent(KeyBasedContent):
    """Content based on the user's language."""

    async def __call__(self, chat_id: int, bot: Bot) -> Optional[str]:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
        except TelegramBadRequest:
            return None
        else:
            return member.user.language_code


@router.message(CommandStart())
async def process_start_command(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    content = LanguageBasedContent(
        default=TextContent(text="Hello!"),
        uk=TextContent(text="Привіт!"),
        ru=TextContent(text="Привет!"),
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
