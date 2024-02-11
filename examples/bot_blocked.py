import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.mailer import Mailer
from aiogram_broadcaster.storage.redis import RedisMailerStorage


TOKEN = "1234:Abc"  # noqa: S105
router = Router(name=__name__)
ACTIVE_CHATS_IDS_TO_MAILING = {
    61043901: True,
    78238238: True,
    78378343: True,
    98765431: True,
    12345678: True,
}


class MailingState(StatesGroup):
    MESSAGE = State()


@router.message(Command("mailing"))
async def on_command_mailing(
    message: Message,
    state: FSMContext,
) -> Any:
    await state.clear()
    await state.set_state(state=MailingState.MESSAGE)
    return await message.answer(text="Send a message:")


@router.message(StateFilter(MailingState.MESSAGE))
async def on_state_message(
    message: Message,
    state: FSMContext,
    broadcaster: Broadcaster,
) -> Any:
    await state.clear()
    mailer = await broadcaster.create_mailer(
        chat_ids=ACTIVE_CHATS_IDS_TO_MAILING,
        message=message,
        delete_on_complete=True,
    )
    await message.answer(text="Run broadcasting...")
    mailer.start()


async def on_failed_sent(error: Exception, chat_id: int) -> None:
    if isinstance(error, TelegramForbiddenError):
        ACTIVE_CHATS_IDS_TO_MAILING[chat_id] = False


async def notify_complete(mailer: Mailer) -> None:
    await mailer.message.reply(text=str(mailer.statistic()))


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    storage = RedisMailerStorage.from_url("redis://localhost:6379")
    broadcaster = Broadcaster(
        bot=bot,
        dispatcher=dispatcher,
        storage=storage,
        auto_setup=True,
    )
    broadcaster.event.failed_sent.register(on_failed_sent)
    broadcaster.event.complete.register(notify_complete)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
