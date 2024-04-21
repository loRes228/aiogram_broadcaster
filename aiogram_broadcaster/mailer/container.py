from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, Optional

from .mailer import Mailer
from .status import MailerStatus


class MailerContainer:
    _mailers: Dict[int, Mailer]

    def __init__(self, *mailers: Mailer) -> None:
        self._mailers = {mailer.id: mailer for mailer in mailers}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(total_mailers={len(self._mailers)})"

    def __str__(self) -> str:
        mailers_string = ", ".join(map(repr, self._mailers.values()))
        return f"{type(self).__name__}[{mailers_string}]"

    def __contains__(self, item: int) -> bool:
        return item in self._mailers

    def __getitem__(self, item: int) -> Mailer:
        return self._mailers[item]

    def __iter__(self) -> Iterator[Mailer]:
        return iter(self.mailers.values())

    def __len__(self) -> int:
        return len(self._mailers)

    def __bool__(self) -> bool:
        if not self._mailers:
            return False
        return all(self._mailers.values())

    def __hash__(self) -> int:
        return hash(frozenset(self._mailers))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MailerContainer):
            return False
        return hash(self) == hash(other)

    @property
    def mailers(self) -> Mapping[int, Mailer]:
        return MappingProxyType(mapping=self._mailers)

    def get_mailer(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    def get_mailers(self, *statuses: MailerStatus) -> List[Mailer]:
        if not statuses:
            return list(self._mailers.values())
        return [mailer for mailer in self._mailers.values() if mailer.status in statuses]
