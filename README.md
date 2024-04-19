## A lightweight aiogram-based library for broadcasting Telegram messages.

## Installation

```bash
pip install git+https://github.com/loRes228/aiogram_broadcaster.git
```

## Creating a mailer and running broadcasting

#### How to create a mailer and initiate broadcasting.

#### Usage:

```python
import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import MessageSendContent
from aiogram_broadcaster.storage import FileMailerStorage

TOKEN = "1234:Abc"
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> Any:
    # Creating content based on the Message
    content = MessageSendContent(message=message)

    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
    )

    # The mailer launch method starts mailing to chats as an asyncio task.
    mailer.start()

    await message.answer(text="Run broadcasting...")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    storage = FileMailerStorage()
    broadcaster = Broadcaster(bot, storage=storage)
    broadcaster.setup(dispatcher=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
```

## Creating a group of mailers based on many bots

#### When using a multibot, it may be necessary to launch many mailings in several bots. For this case, there is a [MailerGroup](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/group.py) object that stores several mailers and can manage them.

#### Usage:

```python
from aiogram import Bot

from aiogram_broadcaster import Broadcaster

# List of bots
bots = [Bot(token="1234:Abc"), Bot(token="5678:Vbn")]

broadcaster = Broadcaster()

# Creating a group of mailers based on several bots
mailer_group = await broadcaster.create_mailers(
    *bots,
    content=...,
    chats=...,
)

# Run all mailers in the mailer group
await mailer_group.run()
```

## Event management system for broadcasting

#### The event system empowers you to effectively manage events throughout the broadcast process.

> **_NOTE:_** `EventRouter` supports chained nesting, similar to
> aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

```python
from aigoram_broadcaster import EventRouter

event = EventRouter(name=__name__)


# Define event handlers


@event.started()
async def mailer_started() -> None:
    """Triggered when the mailer begins its operations."""


@event.stopped()
async def mailer_stopped() -> None:
    """Triggered when the mailer stops its operations."""


@event.completed()
async def mailer_completed() -> None:
    """Triggered when the mailer successfully completes its operations."""


@event.failed_sent()
async def mail_failed_sent() -> None:
    """
    Triggered when a content fails to send.

    Exclusive parameters for this type of event.
        chat_id (int): ID of the chat.
        error (Exception): Exception raised during sending.
    """


@event.success_sent()
async def mail_successful_sent() -> None:
    """
    Triggered when a mail is successfully sent.

    Exclusive parameters for this type of event:
        chat_id (int): ID of the chat.
        response (Any): Response from the sent mail.
    """


# Include the event instance in the broadcaster
broadcaster.event.include(event)
```

## Placeholders for dynamic content insertion

#### Placeholders facilitate the insertion of dynamic content within texts, this feature allows for personalized messaging.

> **_NOTE:_** `Placeholder` supports chained nesting, similar to
> aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

* #### Function-based

```python
from aiogram_broadcaster import PlaceholderRouter

placeholder = PlaceholderRouter(name=__name__)


@placeholder(key="name")
async def get_username(chat_id: int, bot: Bot) -> str:
    """Retrieves the username using the Telegram Bot API."""
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


broadcaster.placeholder.include(placeholder)
```

* #### Class-based

```python
from aiogram_broadcaster import PlaceholderItem


class NamePlaceholder(PlaceholderItem, key="name"):
    async def __call__(self, chat_id: int, bot: Bot) -> str:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
        return member.user.first_name


broadcaster.placeholder.register(NamePlaceholder())
```

* #### Other registration methods

```python
broadcaster.placeholder["name"] = function
broadcaster.placeholder.add(key="key", value="value")
broadcaster.placeholder.attach({"key": "value"}, key="value")
```

### And then

```python
text_content = TextContent(text="Hello, $name!")
photo_content = PhotoContent(photo=..., caption="Photo especially for $name!")
```

## Creating personalized content

#### This module provides utilities to create personalized content targeted to specific users or groups based on their language preferences or geographical location, etc.

> **_NOTE:_** If the default key is not specified, an error will be given if the key is not found.

#### Usage:

```python
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from aiogram_broadcaster.contents import KeyBasedContent, TextContent


class LanguageBasedContent(KeyBasedContent):
    """Content based on the user's language."""

    async def __call__(self, chat_id: int, bot: Bot) -> Optional[str]:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
        except TelegramBadRequest:
            return None
        else:
            return member.user.language_code


content = LanguageBasedContent(
    default=TextContent(text="Hello!"),
    uk=TextContent(text="Привіт!"),
    ru=TextContent(text="Привет!"),
)


class GEOBasedContent(KeyBasedContent):
    """Content based on the user's geographical location."""

    async def __call__(self, chat_id: int, database: Database) -> str:
        user = await database.get_user_by_id(chat_id=chat_id)
        return user.country


content = GEOBasedContent(
    ukraine=TextContent(text="Новини для України!"),
    usa=TextContent(text="News for U.S!"),
)
```

## Tiered dependency injection

#### Utilize in event system, key based content, placeholders, and more for comprehensive management of dependencies.

#### Usage:

* #### Main contextual data

```python
from aiogram_broadcaster import Broadcaster

broadcaster = Broadcaster(key="value")
```

* #### Fetching the dispatcher contextual data

```python
from aiogram import Dispatcher

from aiogram_broadcaster import Broadcaster

dispatcher = Dispatcher()
dispatcher["key"] = "value"

broadcaster = Broadcaster()
broadcaster.setup(dispatcher=dispatcher, fetch_workflow_data=True)
```

* #### Contextual data only for mailer

```python
await broadcaster.create_mailer(content=..., chats=..., key=value)
```

* #### Stored contextual data only for mailer

```python
await broadcaster.create_mailer(content=..., chats=..., data={"key": "value"})
```

* #### Event-to-Event

```python
@event.completed()
async def transfer_content(mailer: Mailer) -> Dict[str, Any]:
    return {"mailer_content": mailer.content}


@event.completed()
async def mailer_completed(mailer_content: BaseContent) -> None:
    print(mailer_content)
```
