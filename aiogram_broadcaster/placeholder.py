from string import Template
from typing import Any, Container, Dict, List, Mapping, Optional, Tuple, TypeVar

from aiogram.dispatcher.event.handler import CallableObject as _CallableObject
from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class CallableObject(_CallableObject):
    async def __call__(self, **kwargs: Any) -> Any:
        return await self.call(**kwargs)


class PlaceholderWizard:
    placeholders: Dict[str, Any]

    def __init__(self, placeholders: Mapping[str, Any]) -> None:
        self.placeholders = {
            key: CallableObject(callback=value) if callable(value) else value
            for key, value in placeholders.items()
        }

    async def fetch_placeholder_data(
        self,
        selection: Container[str],
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            placeholder: await value(**kwargs) if callable(value) else value
            for placeholder, value in self.placeholders.items()
            if placeholder in selection
        }

    def extract_text_field(self, model: BaseModel) -> Optional[Tuple[str, str]]:
        for field in ("caption", "text"):
            if value := getattr(model, field, None):
                return field, value
        return None

    def extract_template_placeholders(
        self,
        template: Template,
        exclude: Optional[Container[str]] = None,
    ) -> List[str]:
        if exclude is None:
            exclude = set()
        return [
            match.group("named")
            for match in template.pattern.finditer(string=template.template)
            if match.group("named") not in exclude
        ]

    async def render(
        self,
        model: ModelType,
        kwargs: Dict[str, Any],
        exclude: Optional[Container[str]] = None,
    ) -> ModelType:
        if not self.placeholders:
            return model
        field = self.extract_text_field(model=model)
        if not field:
            return model
        field_name, filed_value = field
        template = Template(template=filed_value)
        placeholders = self.extract_template_placeholders(
            template=template,
            exclude=exclude,
        )
        if not placeholders:
            return model
        data = await self.fetch_placeholder_data(
            selection=placeholders,
            kwargs=kwargs,
        )
        if not data:
            return model
        rendered_field = {field_name: template.safe_substitute(data)}
        return model.model_copy(update=rendered_field)
