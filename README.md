## A lightweight aiogram-based library for broadcasting Telegram messages.

## Installation

```bash
pip install git+https://github.com/loRes228/aiogram_broadcaster.git
```

## Creating a mailer and running broadcasting

#### How to create a mailer and initiate broadcasting.

#### Usage:

```python
from typing import Any

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.contents import MessageSendContent

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
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    broadcaster = Broadcaster(bot)
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

> **_NOTE:_** Chain nesting is supported, similar to aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

```python
from aigoram_broadcaster import Broadcaster, EventRouter

event = EventRouter(name=__name__)


# Define event handlers


@event.started()
async def on_mailer_started() -> None:
    """Triggered when the mailer begins its operations."""


@event.stopped()
async def on_mailer_stopped() -> None:
    """Triggered when the mailer stops its operations."""


@event.completed()
async def on_mailer_completed() -> None:
    """Triggered when the mailer successfully completes its operations."""


@event.failed_sent()
async def on_failed_mail_sent() -> None:
    """
    Triggered when a message fails to send.

    Exclusive parameters for this type of event.
        chat_id (int): ID of the chat.
        error (Exception): Exception raised during sending.
    """


@event.success_sent()
async def on_successful_mail_sent() -> None:
    """
    Triggered when a message is successfully sent.

    Exclusive parameters for this type of event:
        chat_id (int): ID of the chat.
        response (Any): Response from the sent message.
    """


# Include the event instance in the broadcaster
broadcaster = Broadcaster()
broadcaster.event.include(event)
```

## Placeholders for dynamic content insertion

#### Placeholders facilitate the insertion of dynamic content within texts, this feature allows for personalized messaging.

> **_NOTE:_** Chain nesting is supported, similar to aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

```python
from aiogram import Bot

from aiogram_broadcaster import Broadcaster, Placeholder
from aiogram_broadcaster.contents import PhotoContent, TextContent

broadcaster = Broadcaster()
placeholder = Placeholder(name=__name__)


# Define a function to retrieve the username
@placeholder(key="name")
async def get_username(chat_id: int, bot: Bot) -> str:
    """Retrieves the username using the Telegram Bot API."""
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


# Include the placeholder instance in the broadcaster
broadcaster.placeholder.include(placeholder)

# Other methods for registering placeholders
broadcaster.placeholder["age"] = 22
broadcaster.placeholder.add(key="name", value=get_username)
broadcaster.placeholder.attach({"age": 22}, name=get_username)

# Create content featuring a placeholder
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

#### Utilize in event system, mapping content, placeholders, and more for comprehensive management of dependencies.

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
broadcaster.setup(dispatcher=dispatcher, fetch_data=True)
```

* #### Contextual data only for mailer

```python
broadcaster = Broadcaster()

await broadcaster.create_mailer(content=..., chats=..., key=value)
```

* #### Stored contextual data only for mailer

```python
broadcaster = Broadcaster()

await broadcaster.create_mailer(content=..., chats=..., data={"key": "value"})
```
