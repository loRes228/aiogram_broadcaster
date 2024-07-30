from typing import TYPE_CHECKING, Any

from aiogram_broadcaster.utils.exceptions import DependencyNotFoundError

from .base import BasePlaceholderItem, RenderResult


if TYPE_CHECKING:
    from jinja2.nodes import Template as TemplateNode


try:
    from jinja2 import DebugUndefined, Template
    from jinja2.meta import find_undeclared_variables
except ImportError as error:
    raise DependencyNotFoundError(
        feature_name="JinjaItem",
        module_name="jinja2",
        extra_name="jinja",
    ) from error


class JinjaPlaceholderItem(BasePlaceholderItem):
    name: str
    template_options: dict[str, Any]

    def __init__(self, value: Any, name: str, **template_options: Any) -> None:
        super().__init__(value=value)

        self.name = name
        self.template_options = template_options

    def _render(self, source: str) -> RenderResult:
        template = Template(source=source, undefined=DebugUndefined, **self.template_options)
        if not self._contains_name(template=template, source=source):
            return None
        return {"template": template}, lambda value: template.render({self.name: value})

    def _contains_name(self, template: Template, source: str) -> bool:
        node: TemplateNode = template.environment.parse(source=source)
        return self.name in find_undeclared_variables(ast=node)
