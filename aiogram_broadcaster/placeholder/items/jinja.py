from importlib import import_module
from typing import TYPE_CHECKING, Any

from aiogram_broadcaster.utils.exceptions import DependencyNotFoundError

from .base import BasePlaceholderDecorator, BasePlaceholderEngine, BasePlaceholderItem


if TYPE_CHECKING:
    from typing_extensions import Self

    from aiogram_broadcaster.utils.common_types import WrapperType


class JinjaPlaceholderItem(BasePlaceholderItem):
    name: str

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
        ) -> WrapperType: ...

        def register(
            self,
            value: Any,
            name: str,
        ) -> Self: ...


class JinjaPlaceholderEngine(BasePlaceholderEngine):
    async def render(self, source: str, *items: JinjaPlaceholderItem, **context: Any) -> str:
        from jinja2 import Template  # noqa: PLC0415
        from jinja2.meta import find_undeclared_variables  # noqa: PLC0415

        template = Template(source=source)
        node = template.environment.parse(source=source)
        template_keys: set[str] = find_undeclared_variables(ast=node)
        if not template_keys:
            return source
        data = {
            item.name: await item.get_value(template=template, **context)
            for item in items
            if item.name in template_keys
        }
        if not data:
            return source
        return template.render(data)
