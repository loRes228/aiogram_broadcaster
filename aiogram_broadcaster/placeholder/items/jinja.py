# ruff: noqa: PLC0415

from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable

from aiogram_broadcaster.utils.exceptions import DependencyNotFoundError

from .base import BasePlaceholderDecorator, BasePlaceholderEngine, BasePlaceholderItem


if TYPE_CHECKING:
    from jinja2 import Template
    from typing_extensions import Self


class JinjaPlaceholderItem(BasePlaceholderItem):
    def __init__(self, value: Any, name: str) -> None:
        super().__init__(value=value)

        self.name = name

        try:
            import_module(name="jinja2")
        except ImportError as error:
            raise DependencyNotFoundError(
                feature_name="JinjaPlaceholderItem",
                module_name="jinja2",
                extra_name="jinja",
            ) from error


class JinjaPlaceholderDecorator(BasePlaceholderDecorator):
    __item_class__ = JinjaPlaceholderItem

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


class JinjaPlaceholderEngine(BasePlaceholderEngine):
    async def render(self, source: str, *items: JinjaPlaceholderItem, **context: Any) -> str:
        from jinja2 import Template

        template = Template(source=source)
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
        return template.render(data)

    def get_template_keys(self, template: "Template", source: str) -> set[str]:
        from jinja2.meta import find_undeclared_variables

        node = template.environment.parse(source=source)
        return find_undeclared_variables(ast=node)

    async def get_data(
        self,
        template_keys: set[str],
        *items: JinjaPlaceholderItem,
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
