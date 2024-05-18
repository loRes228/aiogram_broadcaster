from contextlib import suppress
from functools import partial
from typing import NoReturn

from aiogram.dispatcher.event.bases import CancelHandler, SkipHandler


class Interrupt(Exception):  # noqa: N818
    pass


def interrupt() -> NoReturn:
    raise Interrupt


suppress_interrupt = partial(
    suppress,
    Interrupt,
    CancelHandler,
    SkipHandler,
)
