from logging import getLogger

from .event_manager import EventManager
from .mailer import Mailer


logger = getLogger(name="aiogram.broadcaster")


async def on_startup(mailer: Mailer) -> None:
    logger.info("Mailer id=%d is starting.", mailer.id)


async def on_shutdown(mailer: Mailer) -> None:
    logger.info("Mailer id=%d is stopping.", mailer.id)


async def on_complete(mailer: Mailer) -> None:
    logger.info("Mailer id=%d has completed successfully.", mailer.id)


async def on_success_sent(mailer: Mailer, chat_id: int) -> None:
    logger.info(
        "Message successfully sent from mailer id=%d to chat id=%d.",
        mailer.id,
        chat_id,
    )


async def on_failed_sent(mailer: Mailer, chat_id: int, error: Exception) -> None:
    logger.info(
        "Failed to send message from mailer id=%d to chat id=%d. Error: %s",
        mailer.id,
        chat_id,
        error,
    )


def setup_event_logging(event: EventManager) -> None:
    event.startup.register(on_startup)
    event.shutdown.register(on_shutdown)
    event.complete.register(on_complete)
    event.success_sent.register(on_success_sent)
    event.failed_sent.register(on_failed_sent)
