import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import MessageSendContent


TOKENS = ["123:Abc", "456:Obl"]
CHATS = {230912392, 122398104, 39431920120}


router = Router(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> None:
    content = MessageSendContent(message=message)
    mailers = await broadcaster.create_mailers(chats=CHATS, content=content)
    mailers.start()


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bots = [Bot(token=token, default=default) for token in TOKENS]
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(*bots)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(*bots)


if __name__ == "__main__":
    main()
