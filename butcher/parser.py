from inspect import signature
from typing import Any, Generator, NamedTuple, Optional

from .normaiizer import normalize_type


EXCLUDED_NAMED = {
    "self",
    "extra_data",
    "kwargs",
    "chat_id",
    "message_thread_id",
    "reply_parameters",
    "allow_sending_without_reply",
    "reply_to_message_id",
    "disable_web_page_preview",
}


class FieldNode(NamedTuple):
    name: str
    annotation: str
    default: Optional[str] = None


def parse_nodes(obj: Any) -> Generator[FieldNode, None, None]:
    parameters = signature(obj=obj).parameters
    for name, param in parameters.items():
        if name in EXCLUDED_NAMED:
            continue
        yield FieldNode(
            name=name,
            annotation=normalize_type(annotation=param.annotation),
            default=None if param.default is param.empty else str(param.default),
        )
