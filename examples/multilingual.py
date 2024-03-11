import logging
import sys
from typing import Any, Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import TextContent
from aiogram_broadcaster.l10n import BaseLanguageGetter, L10nContentAdapter


TOKEN = "1234:Abc"  # noqa: S105
USERS = {
    78238238: "en",
    78378343: "uk",
    98765431: "de",
    12345678: "pl",
}

router = Router(name=__name__)


@router.message(CommandStart())
async def on_start_command(
    message: Message,
    broadcaster: Broadcaster,
    bot: Bot,
) -> Any:
    content = L10nContentAdapter(
        default=TextContent(text="Hello, world."),
        uk=TextContent(text="Привіт, світ."),
    )
    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USERS,
        bot=bot,
        preserve=False,
    )
    mailer.start()
    await message.answer(text="Run broadcasting...")


class LanguageGetter(BaseLanguageGetter):
    async def __call__(self, chat_id: int) -> Optional[str]:
        return USERS.get(chat_id)


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    language_getter = LanguageGetter()
    broadcaster = Broadcaster(language_getter=language_getter)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
