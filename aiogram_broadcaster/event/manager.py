from typing import Any, Dict

from aiogram_broadcaster.utils.interrupt import suppress_interrupt

from .registry import EventRegistry


class EventManager(EventRegistry):
    __chain_root__ = True

    async def emit_event(self, __event_name: str, /, **context: Any) -> Dict[str, Any]:
        collected_data: Dict[str, Any] = {}
        with suppress_interrupt():
            for registry in self.chain_tail:
                for callback in registry.observers[__event_name].callbacks:
                    result = await callback.call(**context, **collected_data)
                    if result and isinstance(result, dict):
                        collected_data.update(result)
        return collected_data

    async def emit_started(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("started", **context)

    async def emit_stopped(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("stopped", **context)

    async def emit_completed(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("completed", **context)

    async def emit_before_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("before_sent", **context)

    async def emit_success_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("success_sent", **context)

    async def emit_failed_sent(self, **context: Any) -> Dict[str, Any]:
        return await self.emit_event("failed_sent", **context)
