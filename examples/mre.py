import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.mailer import DefaultMailerSettings
from aiogram_broadcaster.storage.file import FileMailerStorage


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> Any:
    # Creating content based on the Message
    content = MessageSendContent(message=message)

    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        destroy_on_complete=True,
    )

    # The mailer launch method starts mailing to chats as an asyncio task.
    mailer.start()

    await message.reply(text="Run broadcasting...")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    storage = FileMailerStorage()
    default = DefaultMailerSettings(interval=1, preserve=True)
    broadcaster = Broadcaster(bot, storage=storage, default=default)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
