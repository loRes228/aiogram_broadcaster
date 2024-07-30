from dataclasses import dataclass
from typing import ClassVar, Literal


class BroadcasterError(Exception):
    pass


class DetailedBroadcasterError(BroadcasterError):
    message: ClassVar[str]

    def __str__(self) -> str:
        return self.message.format_map(vars(self))


@dataclass
class DependencyNotFoundError(DetailedBroadcasterError, ImportError):
    message = (
        "The required dependency '{module_name}' for '{feature_name}' was not found. "
        "To install it, run: `pip install {module_name}` "
        "or via extra: `pip install aiogram_broadcaster[{extra_name}]`."
    )

    feature_name: str
    module_name: str
    extra_name: str


@dataclass
class MailerError(DetailedBroadcasterError, RuntimeError):
    message = "Mailer id {mailer_id} cannot be {operation_name}."

    mailer_id: int
    operation_name: Literal["stopped", "started", "destroyed", "extended", "reset"]
