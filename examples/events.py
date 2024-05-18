import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, EventRouter
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.mailer import Mailer


TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)
event = EventRouter(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    content = MessageSendContent(message=message)
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        bot=bot,
        interval=1,
    )
    mailer.start()


@event.started()
async def mailer_started(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(text="Start broadcasting...")


@event.stopped()
async def mailer_stopped(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(text="Stop broadcasting...")


@event.completed()
async def mailer_completed(mailer: Mailer[MessageSendContent], bot: Bot) -> None:
    await mailer.content.message.as_(bot=bot).reply(
        text=(
            "Broadcasting completed!\n"
            f"Mailer ID: {mailer.id}\n"
            f"{html.blockquote(str(mailer.statistic))}"
        ),
    )


@event.failed_sent()
async def mailer_failed_sent(chat_id: int, error: Exception) -> None:  # noqa: ARG001, RUF029
    if not isinstance(error, TelegramForbiddenError):
        return
    # Do something...


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, default=default)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster()
    broadcaster.event.include(event)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
