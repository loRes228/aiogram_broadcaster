from string import Template
from typing import Any

from .base import BasePlaceholderItem, RenderResult


class StringPlaceholderItem(BasePlaceholderItem):
    name: str

    def __init__(self, value: Any, name: str) -> None:
        super().__init__(value=value)

        self.name = name

    def _render(self, source: str) -> RenderResult:
        template = Template(template=source)
        if not self._contains_name(template=template, source=source):
            return None
        return {"template": template}, lambda value: template.safe_substitute({self.name: value})

    def _contains_name(self, template: Template, source: str) -> bool:
        return any(
            match.group("named") == self.name for match in template.pattern.finditer(string=source)
        )
