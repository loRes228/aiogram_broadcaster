import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import TextContent
from aiogram_broadcaster.placeholder import Placeholder


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}

router = Router(name=__name__)
placeholder = Placeholder()


@router.message(CommandStart())
async def on_command_start(message: Message, broadcaster: Broadcaster) -> Any:
    content = TextContent(text="Hello, $name!")
    mailer = await broadcaster.create_mailer(content=content, chats=USER_IDS)
    mailer.start()
    await message.answer(text="Run broadcasting...")


@placeholder(key="name")
async def name_getter(chat_id: int, bot: Bot) -> str:
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster()
    broadcaster.placeholder.include(placeholder)
    broadcaster.placeholder["static"] = "value"
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
