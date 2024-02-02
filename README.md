# aiogram_broadcaster

## Installation

```bash
pip install git+https://github.com/loRes228/aiogram_broadcaster.git
```

## Usage example

```python
import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.mailer import Mailer

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
        message=message,
        interval=10,
    )
    await message.answer(text="Run broadcasting...")
    await mailer.run()


async def on_complete(mailer: Mailer) -> None:
    statistic = mailer.statistic()
    await mailer.message.reply(
        text=(
            "Successful!\n"
            f"Total chats: {statistic.total_chats}\n"
            f"Success sent: {statistic.success}\n"
            f"Failed sent: {statistic.failed}\n"
            f"Rate: %{statistic.ratio:.2f}"
        ),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot=bot, dispatcher=dispatcher)
    broadcaster.event.complete.register(on_complete)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
```
