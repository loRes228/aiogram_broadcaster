from asyncio import gather, wait
from typing import Any, Coroutine, Dict, Iterable, List

from aiogram_broadcaster.logger import logger

from .container import MailerContainer
from .mailer import Mailer


class MailerGroup(MailerContainer):
    def start(self, **kwargs: Any) -> None:
        for mailer in self._mailers.values():
            try:
                mailer.start(**kwargs)
            except RuntimeError:  # noqa: PERF203
                logger.exception("A start error occurred")

    async def wait(self) -> None:
        futures = [mailer.wait() for mailer in self._mailers.values()]
        await wait(futures)

    async def run(self, **kwargs: Any) -> Dict[Mailer, Any]:
        futures = [mailer.run(**kwargs) for mailer in self._mailers.values()]
        return await self._gather_futures(futures=futures)

    async def stop(self) -> Dict[Mailer, Any]:
        futures = [mailer.stop() for mailer in self._mailers.values()]
        return await self._gather_futures(futures=futures)

    async def destroy(self) -> Dict[Mailer, Any]:
        futures = [mailer.destroy() for mailer in self._mailers.values()]
        return await self._gather_futures(futures=futures)

    async def add_chats(self, chats: Iterable[int]) -> Dict[Mailer, bool]:
        futures = [mailer.add_chats(chats=chats) for mailer in self._mailers.values()]
        return await self._gather_futures(futures=futures)

    async def reset_chats(self) -> None:
        futures = [mailer.reset_chats() for mailer in self._mailers.values()]
        await self._gather_futures(futures=futures)

    async def send(self, chat_id: int) -> Dict[Mailer, Any]:
        futures = [mailer.send(chat_id=chat_id) for mailer in self._mailers.values()]
        return await self._gather_futures(futures=futures)

    async def _gather_futures(self, futures: List[Coroutine[Any, Any, Any]]) -> Dict[Mailer, Any]:
        if not futures:
            return {}
        results = await gather(*futures, return_exceptions=True)
        return dict(zip(self._mailers.values(), results))
