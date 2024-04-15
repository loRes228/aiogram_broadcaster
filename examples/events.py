import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, Event
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.mailer import Mailer


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)
event = Event(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> Any:
    content = MessageSendContent(message=message)
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        data={"publisher_id": message.chat.id, "message_id": message.message_id},
    )
    mailer.start()


@event.started()
async def mailer_started(publisher_id: int, message_id: int, bot: Bot) -> None:
    await bot.send_message(
        chat_id=publisher_id,
        text="Start broadcasting...",
        reply_to_message_id=message_id,
    )


@event.stopped()
async def mailer_stopped(publisher_id: int, message_id: int, bot: Bot) -> None:
    await bot.send_message(
        chat_id=publisher_id,
        text="Stop broadcasting...",
        reply_to_message_id=message_id,
    )


@event.completed()
async def mailer_completed(mailer: Mailer, publisher_id: int, message_id: int, bot: Bot) -> None:
    # fmt: off
    await bot.send_message(
        chat_id=publisher_id,
        text=(
            "Broadcasting completed!\n"
            f"Mailer ID: {mailer.id}\n"
            f"{mailer.statistic}"
        ),
        reply_to_message_id=message_id,
    )
    # fmt: on


@event.failed_sent()
async def mailer_failed_sent(chay_id: int, error: Exception) -> None:  # noqa: ARG001
    if not isinstance(error, TelegramForbiddenError):
        return
    # Do something...


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
    broadcaster.event.include(event)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
