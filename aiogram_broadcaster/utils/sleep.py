from asyncio import Event, TimeoutError, wait_for


async def sleep(event: Event, delay: float) -> bool:
    if event.is_set():
        return False
    try:
        await wait_for(fut=event.wait(), timeout=delay)
    except TimeoutError:
        return True
    else:
        return False
