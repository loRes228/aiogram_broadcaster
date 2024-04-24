import logging
import sys
from typing import Any, Tuple

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import MessageSendContent


TOKENS = {"1234:Abc", "5678:Cdv"}
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


@router.message()
async def process_any_message(
    message: Message,
    broadcaster: Broadcaster,
    bots: Tuple[Bot, ...],
) -> Any:
    content = MessageSendContent(message=message)
    mailers = await broadcaster.create_mailers(
        *bots,
        content=content,
        chats=USER_IDS,
        interval=1,
    )
    mailers.start()
    await message.reply(text="Run broadcasting...")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bots = [Bot(token=token) for token in TOKENS]
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster()
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(*bots)


if __name__ == "__main__":
    main()
