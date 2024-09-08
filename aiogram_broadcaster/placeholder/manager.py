from collections import defaultdict
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from pydantic import BaseModel

from .items.jinja import JinjaPlaceholderEngine, JinjaPlaceholderItem
from .items.regexp import RegexpPlaceholderEngine, RegexpPlaceholderItem
from .items.string import StringPlaceholderEngine, StringPlaceholderItem
from .placeholder import Placeholder


if TYPE_CHECKING:
    from .items.base import BasePlaceholderEngine, BasePlaceholderItem


ModelType = TypeVar("ModelType", bound=BaseModel)

TEXT_FIELDS = {"text", "caption", "title", "description"}


class PlaceholderManager(Placeholder):
    __chain_root__ = True

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name=name)

        self.engines: dict[type[BasePlaceholderItem], BasePlaceholderEngine] = {
            JinjaPlaceholderItem: JinjaPlaceholderEngine(),
            RegexpPlaceholderItem: RegexpPlaceholderEngine(),
            StringPlaceholderItem: StringPlaceholderEngine(),
        }

    async def render(self, model: ModelType, /, **context: Any) -> ModelType:
        if not tuple(self.chain_items):
            return model
        for field_name, field_value in self._parse_text_fields(model=model):
            rendered_field_value = await self._render_source(field_value, **context)
            if rendered_field_value != field_value:
                model = model.model_copy(update={field_name: rendered_field_value})
        return model

    def _parse_text_fields(self, model: BaseModel) -> Generator[tuple[str, str], None, None]:
        mapped_model = dict(model)
        for field_name in TEXT_FIELDS:
            if field_value := mapped_model.get(field_name):
                yield field_name, field_value

    async def _render_source(self, source: str, /, **context: Any) -> str:
        grouped_items = defaultdict(set)
        for item in self.chain_items:
            grouped_items[type(item)].add(item)
        for item_type, items in grouped_items.items():
            source = await self.engines[item_type].render(
                source,
                *items,
                **context,
            )
        return source
