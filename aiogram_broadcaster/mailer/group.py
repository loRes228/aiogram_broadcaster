from asyncio import create_task, gather, wait
from typing import Any, Coroutine, Dict, Iterable, Optional

from .container import MailerContainer
from .mailer import Mailer


class MailerGroup(MailerContainer):
    async def wait(self) -> None:
        futures = [mailer.wait() for mailer in self._mailers.values()]
        await wait(futures)

    def start(self, **kwargs: Any) -> Dict[Mailer, Optional[Exception]]:
        results: Dict[Mailer, Optional[Exception]] = {}
        for mailer in self._mailers.values():
            try:
                mailer.start(**kwargs)
                results[mailer] = None
            except Exception as error:  # noqa: BLE001, PERF203
                results[mailer] = error
        return results

    async def run(self, **kwargs: Any) -> Dict[Mailer, Optional[Exception]]:
        futures = [mailer.run(**kwargs) for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def stop(self) -> Dict[Mailer, Optional[Exception]]:
        futures = [mailer.stop() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def destroy(self) -> Dict[Mailer, Optional[Exception]]:
        futures = [mailer.destroy() for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def add_chats(self, chats: Iterable[int]) -> Dict[Mailer, bool]:
        futures = [mailer.add_chats(chats=chats) for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def reset_chats(self) -> None:
        futures = [mailer.reset_chats() for mailer in self._mailers.values()]
        await self._gather_futures(*futures)

    async def send(self, chat_id: int) -> Dict[Mailer, Any]:
        futures = [mailer.send(chat_id=chat_id) for mailer in self._mailers.values()]
        return await self._gather_futures(*futures)

    async def _gather_futures(self, *futures: Coroutine[Any, Any, Any]) -> Dict[Mailer, Any]:
        if not futures:
            return {}
        tasks = [create_task(future) for future in futures]
        results = await gather(*tasks, return_exceptions=True)
        return dict(zip(self._mailers.values(), results))