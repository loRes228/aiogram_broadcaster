from typing import Any, Callable

from aiogram.dispatcher.event.handler import FilterObject, HandlerObject
from aiogram.filters import Filter
from magic_filter import AttrDict, MagicFilter
from typing_extensions import Self


class MagicContext(Filter):
    """For the magic filters to work properly."""

    def __init__(self, magic_filter: MagicFilter) -> None:
        self.magic_filter = magic_filter

    async def __call__(self, **context: Any) -> Any:
        return self.magic_filter.resolve(value=AttrDict(**context))


class EventObserver:
    def __init__(self) -> None:
        self.handlers: list[HandlerObject] = []

    def __call__(
        self,
        *filters: Callable[..., Any],
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(callback: Callable[..., Any]) -> Callable[..., Any]:
            self.register(callback, *filters)
            return callback

        return wrapper

    def register(self, callback: Callable[..., Any], *filters: Callable[..., Any]) -> Self:
        filters_ = [
            FilterObject(
                callback=(
                    MagicContext(magic_filter=filter_)  # type: ignore[arg-type]
                    if isinstance(filter_, MagicFilter)
                    else filter_
                ),
            )
            for filter_ in filters
        ]
        handler = HandlerObject(callback=callback, filters=filters_)
        self.handlers.append(handler)
        return self
