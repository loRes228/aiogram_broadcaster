from collections.abc import Iterator
from typing import Generic

from aiogram_broadcaster.contents.base import ContentType

from .mailer import Mailer


class MailerContainer(Generic[ContentType]):
    def __init__(self, *mailers: Mailer[ContentType]) -> None:
        self.mailers = {mailer.id: mailer for mailer in mailers}

    def __repr__(self) -> str:
        mailers_string = ", ".join(map(repr, self))
        return f"{type(self).__name__}[{mailers_string}]"

    def __iter__(self) -> Iterator[Mailer[ContentType]]:
        return iter(self.mailers.values())

    def __getitem__(self, item: int) -> Mailer[ContentType]:
        return self.mailers[item]

    def __contains__(self, item: int) -> bool:
        return item in self.mailers

    def __len__(self) -> int:
        return len(self.mailers)
