import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, DefaultMailerProperties
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.event import EventRouter
from aiogram_broadcaster.mailer import Mailer
from aiogram_broadcaster.storage.file import FileBCRStorage


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}

router = Router(name=__name__)
event = EventRouter()


@router.message()
async def on_any_message(message: Message, broadcaster: Broadcaster) -> Any:
    content = MessageSendContent(message=message)
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        data={"publisher_id": message.chat.id, "message_id": message.message_id},
    )
    mailer.start()
    await message.answer(text="Run broadcasting...")


@event.completed()
async def notify_complete(
    mailer: Mailer,
    bot: Bot,
    publisher_id: int,
    message_id: int,
) -> None:
    text = (
        f"Broadcasting has been completed!\n"
        f"Mailer ID: {mailer.id} | Bot ID: {bot.id}\n"
        f"Total chats: {mailer.statistic.total_chats.total}\n"
        f"Failed chats: {mailer.statistic.failed_chats.total}\n"
        f"Success chats: {mailer.statistic.success_chats.total}\n"
    )
    await bot.send_message(
        chat_id=publisher_id,
        text=text,
        reply_to_message_id=message_id,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    bcr_storage = FileBCRStorage()
    default = DefaultMailerProperties(destroy_on_complete=True)
    broadcaster = Broadcaster(bot, storage=bcr_storage, default=default)
    broadcaster.event.include(event)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
