from string import Template
from typing import (
    Any,
    ClassVar,
    Container,
    Dict,
    Iterator,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)

from pydantic import BaseModel

from aiogram_broadcaster.utils.interrupt import suppress_interrupt

from .registry import PlaceholderRegistry


ModelType = TypeVar("ModelType", bound=BaseModel)


class Mappable(Protocol):
    def __iter__(self) -> Iterator[Tuple[str, Any]]: ...


class PlaceholderManager(PlaceholderRegistry):
    __chain_root__ = True

    TEXT_FIELDS: ClassVar[Set[str]] = {"caption", "text"}

    async def fetch_data(self, __select_keys: Container[str], /, **context: Any) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if not __select_keys:
            return data
        for placeholder in self.chain_placeholders:
            if placeholder.key not in __select_keys:
                continue
            with suppress_interrupt():
                data[placeholder.key] = await placeholder.get_value(**context)
        return data

    def extract_text_field(self, model: Mappable) -> Optional[Tuple[str, str]]:
        mapped_model = dict(model)
        for field_name in self.TEXT_FIELDS:
            if (field_value := mapped_model.get(field_name)) and isinstance(field_value, str):
                return field_name, field_value
        return None

    def extract_keys(self, template: Template) -> Set[str]:
        # fmt: off
        return {
            match.group("named")
            for match in template.pattern.finditer(string=template.template)
        }
        # fmt: on

    async def render(
        self,
        __model: ModelType,
        __exclude_keys: Optional[Set[str]] = None,
        /,
        **context: Any,
    ) -> ModelType:
        if __exclude_keys is None:
            __exclude_keys = set()
        self_keys = set(self.chain_keys)
        if not self_keys:
            return __model
        if not self_keys - __exclude_keys:
            return __model
        field = self.extract_text_field(model=__model)
        if not field:
            return __model
        field_name, field_value = field
        template = Template(template=field_value)
        template_keys = self.extract_keys(template=template)
        select_keys = (self_keys & template_keys) - __exclude_keys
        if not select_keys:
            return __model
        data = await self.fetch_data(select_keys, **context)
        if not data:
            return __model
        rendered_field = {field_name: template.safe_substitute(data)}
        return __model.model_copy(update=rendered_field)
