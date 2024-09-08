from aiogram import F
from aiogram.exceptions import TelegramRetryAfter

from aiogram_broadcaster.event.event import Event
from aiogram_broadcaster.mailer.mailer import Mailer
from aiogram_broadcaster.utils.logger import logger
from aiogram_broadcaster.utils.sleep import sleep


async def handle_retry_after(mailer: Mailer, chat_id: int, delay: float) -> None:
    logger.info(
        "Mailer id=%d waiting %.2f seconds to resend the content to chat id=%d.",
        mailer.id,
        delay,
        chat_id,
    )
    if await sleep(event=mailer._stop_event, delay=delay):  # noqa: SLF001
        await mailer.send(chat_id=chat_id)


def setup_retry_after_handler(event: Event) -> Event:
    event.failed_send.register(
        handle_retry_after,
        F.error.cast(type).is_(TelegramRetryAfter),
        F.error.retry_after.as_("delay"),
    )
    return event
