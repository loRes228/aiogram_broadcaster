from collections.abc import Generator
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from aiogram_broadcaster.utils.chain import Chain

from .items.base import BasePlaceholderItem
from .items.jinja import JinjaPlaceholderDecorator
from .items.regexp import RegexpPlaceholderDecorator
from .items.string import StringPlaceholderDecorator


if TYPE_CHECKING:
    from .items.base import BasePlaceholderDecorator


class Placeholder(Chain["Placeholder"], sub_name="placeholder"):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.items: set[BasePlaceholderItem] = set()
        self.jinja = JinjaPlaceholderDecorator(placeholder=self)
        self.regexp = RegexpPlaceholderDecorator(placeholder=self)
        self.string = StringPlaceholderDecorator(placeholder=self)
        self.decorators: dict[str, BasePlaceholderDecorator] = {
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
        self.items.update(items)
        return self
