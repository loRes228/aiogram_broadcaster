from string import Template
from typing import TYPE_CHECKING, Any, Callable

from .base import BasePlaceholderDecorator, BasePlaceholderEngine, BasePlaceholderItem


if TYPE_CHECKING:
    from typing_extensions import Self


class StringPlaceholderItem(BasePlaceholderItem):
    def __init__(self, value: Any, name: str) -> None:
        super().__init__(value=value)

        self.name = name


class StringPlaceholderDecorator(BasePlaceholderDecorator):
    __item_class__ = StringPlaceholderItem

    if TYPE_CHECKING:

        def __call__(
            self,
            name: str,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

        def register(
            self,
            value: Any,
            name: str,
        ) -> Self: ...


class StringPlaceholderEngine(BasePlaceholderEngine):
    async def render(self, source: str, *items: StringPlaceholderItem, **context: Any) -> str:
        template = Template(template=source)
        template_keys = self.get_template_keys(template=template, source=source)
        if not template_keys:
            return source
        data = await self.get_data(
            template_keys,
            *items,
            **context,
            template=template,
        )
        if not data:
            return source
        return template.safe_substitute(data)

    def get_template_keys(self, template: Template, source: str) -> set[str]:
        return {match.group("named") for match in template.pattern.finditer(string=source)}

    async def get_data(
        self,
        template_keys: set[str],
        *items: StringPlaceholderItem,
        **context: Any,
    ) -> dict[str, Any]:
        data = {}
        for item in items:
            if item.name in template_keys:
                continue
            value = await item.get_value(**context)
            if value is not None:
                data[item.name] = value
        return data
