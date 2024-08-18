import typing
from typing import Any, Literal, Optional, Union, _SpecialForm, get_args, get_origin

import aiogram


def normalize_type(annotation: Any) -> str:
    if isinstance(annotation, str):
        annotation = eval(
            annotation,
            {
                **typing.__dict__,
                **aiogram.types.__dict__,
                "Default": aiogram.client.default.Default,
            },
        )

    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation is Ellipsis:
        return "..."

    if origin is set or origin is frozenset or origin is list:
        return f"{origin.__name__.capitalize()}[{normalize_type(annotation=args[0])}]"

    if origin is tuple:
        return f"Tuple[{', '.join(map(normalize_type, args))}]"

    if origin is dict:
        return f"Dict[{normalize_type(annotation=args[0])}, {normalize_type(annotation=args[1])}]"

    if origin is Optional:
        return f"Optional[{normalize_type(annotation=args[0])}]"

    if origin is Union:
        if type(None) in args:
            without_none_args = tuple(arg for arg in args if arg is not type(None))
            return f"Optional[{normalize_type(Union[without_none_args])}]"
        return f"Union[{', '.join(map(normalize_type, args))}]"

    if origin is Literal:
        return f"Literal[{', '.join(map(repr, args))}]"

    if isinstance(annotation, _SpecialForm):
        return annotation._name
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation)
