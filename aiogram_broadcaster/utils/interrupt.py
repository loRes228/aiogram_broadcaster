from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import NoReturn


DEFAULT_STACK_LEVEL = 1


@dataclass
class Interrupt(Exception):  # noqa: N818
    stack_level: int = DEFAULT_STACK_LEVEL


def interrupt(stack_level: int = DEFAULT_STACK_LEVEL) -> NoReturn:
    raise Interrupt(stack_level=stack_level)


@contextmanager
def suppress_interrupt(stack_level: int = DEFAULT_STACK_LEVEL) -> Iterator[None]:
    try:
        yield
    except Interrupt as error:
        if stack_level < error.stack_level:
            raise
