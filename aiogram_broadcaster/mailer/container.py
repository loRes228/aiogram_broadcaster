from typing import Dict, Iterator, List, Optional

from .mailer import Mailer


class MailerContainer:
    _mailers: Dict[int, Mailer]

    def __init__(self, *mailers: Mailer) -> None:
        self._mailers = {mailer.id: mailer for mailer in mailers}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(total_mailers={len(self._mailers)})"

    def __str__(self) -> str:
        mailers = ", ".join(map(repr, self))
        return f"{type(self).__name__}[{mailers}]"

    def __contains__(self, item: int) -> bool:
        return item in self._mailers

    def __getitem__(self, item: int) -> Mailer:
        return self._mailers[item]

    def __iter__(self) -> Iterator[Mailer]:
        return iter(self._mailers.copy().values())

    def __len__(self) -> int:
        return len(self._mailers)

    @property
    def mailers(self) -> Dict[int, Mailer]:
        return self._mailers.copy()

    def get_mailer(self, mailer_id: int) -> Optional[Mailer]:
        return self._mailers.get(mailer_id)

    def get_mailers(self) -> List[Mailer]:
        return list(self._mailers.values())
