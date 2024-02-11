import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster, skip_event
from aiogram_broadcaster.mailer import Mailer
from aiogram_broadcaster.storage.redis import RedisMailerStorage


TOKEN = "1234:Abc"  # noqa: S105
CHATS_IDS_TO_MAILING = [61043901, 78238238, 78378343, 98765431, 12345678]
ADDITIONAL_CHAT_IDS = [11043901, 78333383, 99372323, 12756556, 56563681]

router = Router(name=__name__)


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
        chat_ids=CHATS_IDS_TO_MAILING,
        message=message,
        delete_on_complete=True,
    )
    await message.answer(text="Run broadcasting...")
    mailer.start()


async def append_chats(mailer: Mailer) -> None:
    if await mailer.add_chats(chat_ids=ADDITIONAL_CHAT_IDS):
        await mailer.run()
        skip_event()


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
    broadcaster.event.complete.register(append_chats)
    broadcaster.event.complete.register(notify_complete)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
