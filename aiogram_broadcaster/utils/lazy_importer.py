from importlib import import_module
from typing import Any, Callable


def lazy_importer(package: str, **modules: str) -> Callable[[str], Any]:
    def wrapper(name: str) -> Any:
        if name not in modules:
            raise AttributeError
        module = import_module(name=modules[name], package=package)
        return getattr(module, name)

    return wrapper
