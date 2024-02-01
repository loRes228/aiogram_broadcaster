class BroadcasterError(Exception):
    pass


class MailerNotExistsError(BroadcasterError):
    pass


class MailerAlreadyStartedError(BroadcasterError):
    pass


class MailerAlreadyStoppedError(BroadcasterError):
    pass


class MailerHasBeenCompletedError(BroadcasterError):
    pass


class MailerHasBeenDeletedError(BroadcasterError):
    pass
