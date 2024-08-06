from typing import Any

from aiogram_broadcaster.utils.interrupt import suppress_interrupt

from .event import Event


class EventManager(Event):
    __chain_root__ = True

    async def emit_event(self, event_name: str, /, **context: Any) -> None:
        with suppress_interrupt():
            for event in self.chain_tail:
                with suppress_interrupt(stack_level=1):
                    for handler in event.observers[event_name].handlers:
                        filter_result, filter_data = await handler.check(**context)
                        if not filter_result:
                            continue
                        context.update(filter_data)
                        handler_result = await handler.call(**context)
                        if isinstance(handler_result, dict):
                            context.update(handler_result)

    async def emit_created(self, **context: Any) -> None:
        await self.emit_event("created", **context)

    async def emit_destroyed(self, **context: Any) -> None:
        await self.emit_event("destroyed", **context)

    async def emit_started(self, **context: Any) -> None:
        await self.emit_event("started", **context)

    async def emit_stopped(self, **context: Any) -> None:
        await self.emit_event("stopped", **context)

    async def emit_completed(self, **context: Any) -> None:
        await self.emit_event("completed", **context)

    async def emit_failed_send(self, **context: Any) -> None:
        await self.emit_event("failed_send", **context)

    async def emit_success_send(self, **context: Any) -> None:
        await self.emit_event("success_send", **context)
