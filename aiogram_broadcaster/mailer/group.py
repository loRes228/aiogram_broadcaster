from asyncio import create_task, gather, wait
from typing import Any, Coroutine, Dict, Iterable, Optional, Set, Union

from .container import MailerContainer
from .mailer import Mailer


class MailerGroup(MailerContainer):
    def start(self) -> Dict[Mailer, Optional[Exception]]:
        results: Dict[Mailer, Optional[Exception]] = {}
        for mailer in self._mailers.values():
            try:
                mailer.start()
                results[mailer] = None
            except Exception as error:  # noqa: BLE001, PERF203
                results[mailer] = error
        return results

    async def wait(self) -> None:
        futures = [mailer.wait() for mailer in self._mailers.values()]
        await wait(futures)

    async def run(self) -> Dict[Mailer, Union[Exception, bool]]:
        futures = [mailer.run() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def stop(self) -> Dict[Mailer, Optional[Exception]]:
        futures = [mailer.stop() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def destroy(self) -> Dict[Mailer, Optional[Exception]]:
        futures = [mailer.destroy() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def add_chats(self, chats: Iterable[int]) -> Dict[Mailer, Union[Exception, Set[int]]]:
        futures = [mailer.add_chats(chats=chats) for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def reset_chats(self) -> Dict[Mailer, Union[Exception, bool]]:
        futures = [mailer.reset_chats() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def send(self, chat_id: int) -> Dict[Mailer, Any]:
        futures = [mailer.send(chat_id=chat_id) for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def _gather_futures(self, *futures: Coroutine[Any, Any, Any]) -> Dict[Mailer, Any]:
        if not futures:
            return {}
        tasks = [create_task(future) for future in futures]
        results = await gather(*tasks, return_exceptions=True)
        return dict(zip(self._mailers.values(), results))
