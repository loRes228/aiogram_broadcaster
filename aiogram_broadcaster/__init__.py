__all__ = (
    "Broadcaster",
    "DefaultMailerProperties",
    "EventRouter",
    "Mailer",
    "MailerStatistic",
    "MailerStatus",
    "PlaceholderItem",
    "PlaceholderRouter",
    "__version__",
    "skip_event",
)

from .__meta__ import __version__
from .broadcaster import Broadcaster
from .default_properties import DefaultMailerProperties
from .event import EventRouter, skip_event
from .mailer.mailer import Mailer
from .mailer.statistic import MailerStatistic
from .mailer.status import MailerStatus
from .placeholder import PlaceholderItem, PlaceholderRouter
