from string import Template
from typing import TYPE_CHECKING, Any

from .base import BasePlaceholderDecorator, BasePlaceholderEngine, BasePlaceholderItem


if TYPE_CHECKING:
    from typing_extensions import Self

    from aiogram_broadcaster.utils.common_types import WrapperType


class StringPlaceholderItem(BasePlaceholderItem):
    name: str

    def __init__(self, value: Any, name: str) -> None:
        super().__init__(value=value)

        self.name = name


class StringPlaceholderDecorator(BasePlaceholderDecorator):
    __item_class__ = StringPlaceholderItem

    if TYPE_CHECKING:

        def __call__(
            self,
            name: str,
        ) -> WrapperType: ...

        def register(
            self,
            value: Any,
            name: str,
        ) -> Self: ...


class StringPlaceholderEngine(BasePlaceholderEngine):
    async def render(self, source: str, *items: StringPlaceholderItem, **context: Any) -> str:
        template = Template(template=source)
        template_keys = {
            match.group("named") for match in template.pattern.finditer(string=source)
        }
        if not template_keys:
            return source
        data = {
            item.name: await item.get_value(template=template, **context)
            for item in items
            if item.name in template_keys
        }
        if not data:
            return source
        return template.safe_substitute(data)
