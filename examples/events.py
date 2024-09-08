import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, Event, Mailer
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.intervals import SimpleInterval
from aiogram_broadcaster.utils.retry_after_handler import setup_retry_after_handler


TOKEN = "123:Abc"
CHATS = {230912392, 122398104, 39431920120}


router = Router(name=__name__)
event = Event(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> None:
    content = MessageSendContent(message=message)
    interval = SimpleInterval(interval=0.4)
    mailer = await broadcaster.create_mailer(
        chats=CHATS,
        content=content,
        interval=interval,
        destroy_on_complete=True,
    )
    mailer.start()


@event.started()
async def process_mailer_started(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(text="Broadcasting started.")


@event.stopped()
async def process_mailer_stopped(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(text="Broadcasting stopped.")


@event.completed()
async def process_mailer_completed(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(
        text=(
            "Broadcasting completed.\n"
            f"Total chats: {len(mailer.chats.total)}\n"
            f"Processed chats: {len(mailer.chats.processed)} | "
            f"{mailer.chats.processed % mailer.chats.total:.2f}%\n"
            f"Pending chats: {len(mailer.chats.pending)} | "
            f"{mailer.chats.pending % mailer.chats.total:.2f}%\n"
            f"Failed chats: {len(mailer.chats.failed)} | "
            f"{mailer.chats.failed % mailer.chats.total:.2f}%\n"
            f"Success chats: {len(mailer.chats.success)} | "
            f"{mailer.chats.success % mailer.chats.total:.2f}%\n"
        ),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, default=default)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
    broadcaster.setup(dispatcher=dispatcher)
    broadcaster.event.bind(event)
    setup_retry_after_handler(event=broadcaster.event)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
