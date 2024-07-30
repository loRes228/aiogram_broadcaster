from asyncio import Task, gather
from collections.abc import Coroutine, Iterable
from typing import Any, Optional, Union

from aiogram_broadcaster.contents.base import ContentType

from .container import MailerContainer
from .mailer import Mailer


class MailerGroup(MailerContainer[ContentType]):
    async def destroy(self) -> dict[Mailer[ContentType], Optional[BaseException]]:
        return await self._emit(mailer.destroy() for mailer in self)

    async def stop(self) -> dict[Mailer[ContentType], Optional[BaseException]]:
        return await self._emit(mailer.stop() for mailer in self)

    def start(self) -> dict[Mailer[ContentType], Union[Task[bool], BaseException]]:
        results: dict[Mailer[ContentType], Union[Task[bool], BaseException]] = {}
        for mailer in self:
            try:
                results[mailer] = mailer.start()
            except BaseException as error:  # noqa: BLE001, PERF203
                results[mailer] = error
        return results

    async def extend(
        self,
        chats: Iterable[int],
    ) -> dict[Mailer[ContentType], Union[set[int], BaseException]]:
        return await self._emit(mailer.extend(chats=chats) for mailer in self)

    async def reset(self) -> dict[Mailer[ContentType], Optional[BaseException]]:
        return await self._emit(mailer.reset() for mailer in self)

    async def send(
        self,
        chat_id: int,
        *,
        disable_placeholders: bool = False,
        disable_error_handling: bool = False,
    ) -> dict[Mailer[ContentType], Union[tuple[bool, Any], BaseException]]:
        return await self._emit(
            mailer.send(
                chat_id=chat_id,
                disable_placeholders=disable_placeholders,
                disable_error_handling=disable_error_handling,
            )
            for mailer in self
        )

    async def _emit(
        self,
        targets: Iterable[Coroutine[Any, Any, Any]],
    ) -> dict[Mailer[ContentType], Any]:
        if not targets:
            return {}
        results = await gather(*targets, return_exceptions=True)
        return dict(zip(self, results))
