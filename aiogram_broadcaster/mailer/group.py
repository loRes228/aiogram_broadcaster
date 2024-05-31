from asyncio import ensure_future, gather, wait
from typing import Any, Coroutine, Dict, Iterable, Optional, Set, Union

from .container import MailerContainer
from .mailer import Mailer


class MailerGroup(MailerContainer):
    def start(self) -> Dict[Mailer, Optional[Exception]]:
        results: Dict[Mailer, Optional[Exception]] = {}
        for mailer in self:
            try:
                mailer.start()
                results[mailer] = None
            except Exception as error:  # noqa: BLE001, PERF203
                results[mailer] = error
        return results

    async def wait(self) -> None:
        if not self._mailers:
            return
        await wait(ensure_future(mailer.wait()) for mailer in self)

    async def run(self) -> Dict[Mailer, Union[Exception, bool]]:
        return await self._gather_targets(mailer.run() for mailer in self)

    async def stop(self) -> Dict[Mailer, Optional[Exception]]:
        return await self._gather_targets(mailer.stop() for mailer in self)

    async def destroy(self) -> Dict[Mailer, Optional[Exception]]:
        return await self._gather_targets(mailer.destroy() for mailer in self)

    async def add_chats(self, chats: Iterable[int]) -> Dict[Mailer, Union[Exception, Set[int]]]:
        return await self._gather_targets(mailer.add_chats(chats=chats) for mailer in self)

    async def reset_chats(self) -> Dict[Mailer, Union[Exception, bool]]:
        return await self._gather_targets(mailer.reset_chats() for mailer in self)

    async def send(self, chat_id: int) -> Dict[Mailer, Any]:
        return await self._gather_targets(mailer.send(chat_id=chat_id) for mailer in self)

    async def _gather_targets(
        self,
        targets: Iterable[Coroutine[Any, Any, Any]],
    ) -> Dict[Mailer, Any]:
        if not targets:
            return {}
        results = await gather(*targets, return_exceptions=True)
        return dict(zip(self, results))
