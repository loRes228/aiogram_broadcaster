from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from aiogram_broadcaster.utils.interrupt import suppress_interrupt

from .placeholder import Placeholder


ModelType = TypeVar("ModelType", bound=BaseModel)

TEXT_FIELDS = {"text", "caption"}


class PlaceholderManager(Placeholder):
    __chain_root__ = True

    async def render(self, model: ModelType, /, **context: Any) -> ModelType:
        if not tuple(self.chain_items):
            return model
        field: Optional[tuple[str, str]] = self._extract_text_field(model=model)
        if not field:
            return model
        field_name, field_value = field
        rendered_value: str = await self._render_source(field_value, **context)
        return model.model_copy(update={field_name: rendered_value})

    def _extract_text_field(self, model: BaseModel) -> Optional[tuple[str, str]]:
        mapped_model = dict(model)
        for field_name in TEXT_FIELDS:
            if field_value := mapped_model.get(field_name):
                return field_name, field_value
        return None

    async def _render_source(self, source: str, /, **context: Any) -> str:
        with suppress_interrupt(stack_level=2):
            for item in self.chain_items:
                with suppress_interrupt(stack_level=1):
                    source = await item.render(source, **context)
        return source
