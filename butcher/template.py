from jinja2 import Template


TEMPLATE = Template(
    source="""
# THIS CODE WAS AUTO-GENERATED VIA `butcher`

from typing import {{ typing_all|join(', ') }}
from datetime import datetime, timedelta

from aiogram.types import {{ aiogram_types_all|join(', ') }}
from aiogram.methods import {{ aiogram_methods_all|join(', ') }}
from aiogram.client.default import Default

from .base import BaseContent


class {{ content_name }}(BaseContent):
    {% if model_extra_nodes is not none %}
    {% for node in model_extra_nodes %}
    {{ node.name }}: {{ node.annotation }}{% if node.default is not none %} = {{ node.default }}{% endif %}\n
    {% endfor %}
    {% endif %}
    {% for node in nodes %}
    {{ node.name }}: {{ node.annotation }}{% if node.default is not none %} = {{ node.default }}{% endif %}\n
    {% endfor %}

    async def __call__(self, chat_id: int) -> {{ call_result }}:
        return {{ method_exec }}(
            chat_id=chat_id,
            {% for node in nodes %}
            {{ node.name }}=self.{{ node.name }},
            {% endfor %}
            {% if put_model_extra %}
            **(self.model_extra or {}),
            {% endif %}
        )

    if TYPE_CHECKING:
        def __init__(
            self,
            *,
            {% if model_extra_nodes is not none %}
            {% for node in model_extra_nodes %}
            {{ node.name }}: {{ node.annotation }}{% if node.default is not none %} = ...{% endif %},
            {% endfor %}
            {% endif %}
            {% for node in nodes %}
            {{ node.name }}: {{ node.annotation }}{% if node.default is not none %} = ...{% endif %},
            {% endfor %}
            **kwargs: Any,
        ) -> None: ...
""",
    trim_blocks=True,
    lstrip_blocks=True,
)


INIT_TEMPLATE = Template(
    source="""
__all__ = (
    {% set names = ['"BaseContent"', '"adapters"'] %}
    {% for target in targets %}
        {% set _ = names.append('"' + target.content_name + '"') %}
    {% endfor %}
    {{ names | join(', ') }}
)


from . import adapters
from .base import BaseContent
{% for target in targets %}
from .{{ target.content_file_name }} import {{ target.content_name }}
{% endfor %}
""",
    trim_blocks=True,
    lstrip_blocks=True,
)
