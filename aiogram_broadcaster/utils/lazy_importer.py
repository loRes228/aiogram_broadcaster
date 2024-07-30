from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable


if TYPE_CHECKING:
    from types import ModuleType


def lazy_importer(package: str, **modules: str) -> Callable[[str], Any]:
    def wrapper(name: str) -> Any:
        if name not in modules:
            raise AttributeError
        module: ModuleType = import_module(name=modules[name], package=package)
        return getattr(module, name)

    return wrapper
