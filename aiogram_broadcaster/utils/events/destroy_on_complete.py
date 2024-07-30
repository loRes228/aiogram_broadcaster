from aiogram import F

from aiogram_broadcaster.event.event import Event
from aiogram_broadcaster.mailer.mailer import Mailer


event = Event(name=__name__)


@event.completed(F.destroy_on_complete)
async def destroy_on_complete(mailer: Mailer) -> None:
    await mailer.destroy()
