from .__meta__ import __version__
from .broadcaster import Broadcaster
from .default import DefaultMailerProperties
from .event import EventRouter, skip_event
from .mailer.mailer import Mailer
from .mailer.statistic import MailerStatistic
from .mailer.status import MailerStatus
from .placeholder import PlaceholderItem, PlaceholderRouter


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
