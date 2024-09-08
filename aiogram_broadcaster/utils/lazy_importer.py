from importlib import import_module
from typing import Any, Callable


def lazy_importer(package: str, **targets: str) -> Callable[[str], Any]:
    def wrapper(name: str) -> Any:
        if name not in targets:
            raise AttributeError
        module = import_module(name=targets[name], package=package)
        return getattr(module, name)

    return wrapper
