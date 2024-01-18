import logging
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from redis.asyncio import Redis

from aiogram_broadcaster import Broadcaster


TOKEN = "1234:Abc"  # noqa: S105
CHATS_IDS_TO_MAILING = [123, 456, 789]

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
    mailer = await broadcaster.create(
        chat_ids=CHATS_IDS_TO_MAILING,
        message_id=message.message_id,
        from_chat_id=message.chat.id,
        interval=10,
    )
    await message.answer(text="Run broadcasting...")
    await mailer.run()
    statistic = mailer.statistic()

    return await message.reply(
        text=(
            "Successful!\n"
            f"Total chats: {statistic.total_chats}\n"
            f"Success sent: {statistic.success}\n"
            f"Failed sent: {statistic.failed}\n"
            f"Rate: %{statistic.ratio:.2f}"
        ),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    redis = Redis(decode_responses=True)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot=bot, redis=redis)
    broadcaster.setup(dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
