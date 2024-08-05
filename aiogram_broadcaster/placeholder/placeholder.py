from collections.abc import Generator
from typing import Optional

from typing_extensions import Self

from aiogram_broadcaster.utils.chain import Chain

from .items.base import BasePlaceholderDecorator, BasePlaceholderItem
from .items.jinja import JinjaPlaceholderDecorator
from .items.regexp import RegexpPlaceholderDecorator
from .items.string import StringPlaceholderDecorator


class Placeholder(Chain["Placeholder"], sub_name="placeholder"):
    items: list[BasePlaceholderItem]
    jinja: JinjaPlaceholderDecorator
    regexp: RegexpPlaceholderDecorator
    string: StringPlaceholderDecorator
    decorators: dict[str, BasePlaceholderDecorator]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.items = []
        self.jinja = JinjaPlaceholderDecorator(placeholder=self)
        self.regexp = RegexpPlaceholderDecorator(placeholder=self)
        self.string = StringPlaceholderDecorator(placeholder=self)
        self.decorators = {
            "jinja": self.jinja,
            "regexp": self.regexp,
            "string": self.string,
        }

    @property
    def chain_items(self) -> Generator[BasePlaceholderItem, None, None]:
        for placeholder in self.chain_tail:
            yield from placeholder.items

    def register(self, *items: BasePlaceholderItem) -> Self:
        if not items:
            raise ValueError("At least one item must be provided to register.")
        self.items.extend(items)
        return self
