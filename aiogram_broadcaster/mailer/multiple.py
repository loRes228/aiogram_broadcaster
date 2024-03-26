from asyncio import gather, wait
from typing import Any, Coroutine, Dict, Iterable, Iterator, List, Tuple

from aiogram_broadcaster.logger import logger

from .mailer import Mailer


class MultipleMailers:
    mailers: Tuple[Mailer, ...]

    def __init__(self, mailers: Iterable[Mailer]) -> None:
        self.mailers = tuple(mailers)

    def __iter__(self) -> Iterator[Mailer]:
        return iter(self.mailers)

    def __len__(self) -> int:
        return len(self.mailers)

    def __repr__(self) -> str:
        return f"MultipleMailers(total_mailers={len(self.mailers)})"

    def __str__(self) -> str:
        mailers = ", ".join(map(repr, self.mailers))
        return f"MultipleMailers[{mailers}]"

    def start(self, **kwargs: Any) -> None:
        for mailer in self.mailers:
            try:
                mailer.start(**kwargs)
            except RuntimeError:  # noqa: PERF203
                logger.exception("A start error occurred")

    async def wait(self) -> None:
        futures = [mailer.wait() for mailer in self.mailers]
        await wait(futures)

    async def run(self, **kwargs: Any) -> Dict[Mailer, Any]:
        futures = [mailer.run(**kwargs) for mailer in self.mailers]
        return await self._gather_futures(futures=futures)

    async def stop(self) -> Dict[Mailer, Any]:
        futures = [mailer.stop() for mailer in self.mailers]
        return await self._gather_futures(futures=futures)

    async def destroy(self) -> Dict[Mailer, Any]:
        futures = [mailer.destroy() for mailer in self.mailers]
        return await self._gather_futures(futures=futures)

    async def add_chats(self, chats: Iterable[int]) -> Dict[Mailer, bool]:
        futures = [mailer.add_chats(chats=chats) for mailer in self.mailers]
        return await self._gather_futures(futures=futures)

    async def send_content(self, chat_id: int) -> Dict[Mailer, Any]:
        futures = [mailer.send_content(chat_id=chat_id) for mailer in self.mailers]
        return await self._gather_futures(futures=futures)

    async def _gather_futures(self, futures: List[Coroutine[Any, Any, Any]]) -> Dict[Mailer, Any]:
        if not futures:
            return {}
        results = await gather(*futures, return_exceptions=True)
        return dict(zip(self.mailers, results))
