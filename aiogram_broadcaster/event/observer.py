from typing import Callable, Iterator, List

from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from typing_extensions import Self


class EventObserver:
    callbacks: List[CallableObject]

    def __init__(self) -> None:
        self.callbacks = []

    def __iter__(self) -> Iterator[CallbackType]:
        return iter(callback.callback for callback in self.callbacks)

    def __len__(self) -> int:
        return len(self.callbacks)

    def __call__(self) -> Callable[[CallbackType], CallbackType]:
        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback)
            return callback

        return wrapper

    def register(self, *callbacks: CallbackType) -> Self:
        if not callbacks:
            raise ValueError("At least one callback must be provided to register.")
        self.callbacks.extend(CallableObject(callback=callback) for callback in callbacks)
        return self
