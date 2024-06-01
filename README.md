# aiogram_broadcaster

[![GitHub License](https://img.shields.io/github/license/loRes228/aiogram_broadcaster?style=plastic&logo=github&link=https%3A%2F%2Fgithub.com%2FloRes228%2Faiogram_broadcaster%3Ftab%3DMIT-1-ov-file)](https://github.com/loRes228/aiogram_broadcaster?tab=MIT-1-ov-file#MIT-1-ov-file)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/loRes228/aiogram_broadcaster/tests.yml?branch=main&style=plastic&logo=github)](https://github.com/loRes228/aiogram_broadcaster/actions)
[![PyPI - Status](https://img.shields.io/pypi/status/aiogram-broadcaster?style=plastic&logo=pypi)](https://pypi.org/project/aiogram-broadcaster/)
[![PyPI - Version](https://img.shields.io/pypi/v/aiogram-broadcaster?style=plastic&color=blue&logo=pypi)](https://pypi.org/project/aiogram-broadcaster/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aiogram-broadcaster?style=plastic&color=green&logo=pypi)](https://pypi.org/project/aiogram-broadcaster/)
[![PyPI - Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=plastic&logo=python)](https://www.python.org/downloads/)
[![Static Badge](https://img.shields.io/badge/aiogram-3.6%2B-blue?style=plastic&logoColor=blue&link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F&logo=pypi)](https://aiogram.dev)

### **aiogram_broadcaster** is lightweight aiogram-based library for broadcasting Telegram messages.

## Features

* #### [Event system](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#event-system-1)
* #### [Placeholders](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#placeholders) (variables in texts)
* #### Flexible contents ([LazyContent](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#lazy-content), [KeyBasedContent](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#key-based-content))
* #### [Storages](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#storages-1)
* #### [Statistics](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#statistic-mailerstatistic-instance-containing-statistics-about-the-mailers-performance)
* #### [Statuses](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#status-current-status-of-the-mailer-eg-started-stopped-completed)
* #### Supports [multiple mailings](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#mailer)
* #### Supports [multibot](https://github.com/loRes228/aiogram_broadcaster?tab=readme-ov-file#multibot)

## Installation

* #### From PyPI

```commandline
pip install --upgrade aiogram-broadcaster
```

* #### From GitHub (_Development build_)

```commandline
pip install https://github.com/loRes228/aiogram_broadcaster/archive/refs/heads/dev.zip --fore-reinstall
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
from aiogram_broadcaster.storages.file import FileMailerStorage

TOKEN = "1234:Abc"
USER_IDS = {78238238, 78378343, 98765431, 12345678}

router = Router(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster) -> Any:
    # Creating content based on the Message
    content = MessageSendContent(message=message)

    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        interval=1,
        preserve=True,
        destroy_on_complete=True,
    )

    # The mailer launch method starts mailing to chats as an asyncio task.
    mailer.start()

    await message.reply(text="Run broadcasting...")


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

## Mailer

#### The [Mailer](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/mailer.py) class facilitates the broadcasting of messages to multiple chats in Telegram. It manages the lifecycle of the broadcast process, including starting, stopping, and destroying the broadcast.

#### Properties

* #### id: Unique identifier for the mailer.
* #### status: Current [mailer status](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/status.py) of the mailer (e.g., STARTED, STOPPED, COMPLETED).
* #### settings: Configuration settings for the mailer.
* #### statistic: Statistic instance containing statistics about the mailer's performance.
* #### content: Content to be broadcast.
* #### context: Additional context data used during the broadcasting process.
* #### bot: aiogram Bot instance used for interacting with the Telegram API.

#### Methods

* #### send(chat_id: int) -> Any: Sends the content to a specific chat identified by chat_id.
* #### add_chats(chats: Iterable[int]) -> Set[int]: Adds new chats to the mailer's registry.
* #### reset_chats() -> bool: Resets the state of all chats.
* #### destroy() -> None: Destroys the mailer instance and cleans up resources.
* #### stop() -> None: Stops the broadcasting process.
* #### run() -> bool: Initiates the broadcasting process.
* #### start() -> None: Starts the broadcasting process in background.
* #### wait() -> None: Waits for the broadcasting process to complete.

#### Usage:

```python
mailer = await broadcaster.create_mailer(content=..., chats=...)
try:
    logging.info("Mailer starting...")
    await mailer.run()
finally:
    logging.info("Mailer shutdown...")
    await mailer.destroy()
```

## Multibot

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

## Event system

#### The event system empowers you to effectively manage events throughout the broadcast process.

> [!NOTE]
> `EventRegistry` supports chained nesting, similar to aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

```python
from aigoram_broadcaster import EventRegistry

event = EventRegistry(name=__name__)


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


@event.before_sent()
async def mail_before_sent() -> None:
    """
    Triggered before sending content.

    Exclusive parameters for this type of event.
        chat_id (int): ID of the chat.
    """


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
broadcaster.event.bind(event)
```

## Placeholders

#### Placeholders facilitate the insertion of dynamic content within texts, this feature allows for personalized messaging.

> [!NOTE]
> `PlaceholderRegistry` supports chained nesting, similar to
> aiogram [Router](https://docs.aiogram.dev/en/latest/dispatcher/router.html#nested-routers).

#### Usage:

* #### Function-based

```python
from aiogram_broadcaster import PlaceholderRegistry

placeholder = PlaceholderRegistry(name=__name__)


@placeholder(key="name")
async def get_username(chat_id: int, bot: Bot) -> str:
    """Retrieves the username using the Telegram Bot API."""
    member = await bot.get_chat_member(chat_id=chat_id, user_id=chat_id)
    return member.user.first_name


broadcaster.placeholder.bind(placeholder)
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
placeholder["name"] = function
placeholder.add({"key": "value"}, name=function)
```

### And then

```python
text_content = TextContent(text="Hello, $name!")
photo_content = PhotoContent(photo=..., caption="Photo especially for $name!")
```

## Key-based content

#### This module provides utilities to create personalized content targeted to specific users or groups based on their language preferences or geographical location, etc.

> [!NOTE]
> If the default key is not specified, an error will be given if the key is not found.

#### Usage:

```python
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
    # default=TextContent(text="Hello!"),
    uk=TextContent(text="Привіт!"),
    ru=TextContent(text="Привет!"),
)
```

## Lazy content

#### Allows content to be generated dynamically at the time the message is sent.

#### Usage:

```python
from secrets import choice
from typing import List

from pydantic import SerializeAsAny

from aiogram_broadcaster.contents import BaseContent, LazyContent, TextContent


class RandomizedContent(LazyContent):
    contents: List[SerializeAsAny[BaseContent]]

    async def __call__(self) -> BaseContent:
        return choice(self.contents)


content = RandomizedContent(
    contents=[
        TextContent(text="Hello!"),
        TextContent(text="Hi!"),
    ],
)
await broadcaster.create_mailer(content=content, chats=...)
```

## Dependency injection

#### It is used for comprehensive dependency management, used in event system, key-based/lazy content, placeholders and so on.

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
broadcaster.setup(dispatcher, fetch_dispatcher_context=True)
```

* #### Contextual data only for mailer

```python
await broadcaster.create_mailer(content=..., chats=..., key=value)
```

* #### Stored contextual data only for mailer

```python
await broadcaster.create_mailer(content=..., chats=..., stored_context={"key": "value"})
```

* #### Event-to-event

```python
@event.completed()
async def transfer_content() -> Dict[str, Any]:
    return {"my_data": 1}


@event.completed()
async def mailer_completed(my_data: 1) -> None:
    print(my_data)
```

## Storages

#### Storage allow you to save mailer states to external storage.

* #### [BaseMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storages/base.py) Abstract class of storage.
* #### [FileMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storages/file.py) Saves the mailers to a file.
* #### [MongoDBMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storages/mongodb.py) Saves the mailers to a MongoDB. (Extra: mongo)
* #### [RedisMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storages/redis.py) Saves the mailers to a Redis. (Extra: redis)
* #### [SQLAlchemyMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storages/sqlalchemy.py) Saves the mailers using SQLAlchemy. (Extra: sqlalchemy)

#### Usage:

```python
from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.storages.redis import RedisMailerStorage

# from aiogram_broadcaster.storages.file import FileMailerStorage
# from aiogram_broadcaster.storages.mongodb import MongoDBMailerStorage
# from aiogram_broadcaster.storages.sqlalchemy import SQLAlchemyMailerStorage

# storages = FileMailerStorage()
# storages = MongoDBMailerStorage.from_url(url="mongodb://localhost:27017")
# storages = SQLAlchemyMailerStorage.from_url(url="sqlite+aiosqlite:///database.db")

storage = RedisMailerStorage.from_url(url="redis://localhost:6379")
broadcaster = Broadcaster(storage=storage)
```

## Default mailer settings

#### The [DefaultMailerSettings](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/settings.py) class defines the default properties for mailers created within the broadcaster. It allows setting various parameters like interval, dynamic_interval, run_on_startup, handle_retry_after, destroy_on_complete, and preserve. These properties provide flexibility and control over the behavior of mailers.

#### Parameters:

* #### interval: The interval (in seconds) between successive message broadcasts. It defaults to 0, indicating immediate broadcasting.
* #### dynamic_interval: A boolean flag indicating whether the interval should be adjusted dynamically based on the number of chats. If set to True, the interval will be divided equally among the chats.
* #### run_on_startup: A boolean flag indicating whether the mailer should start broadcasting messages automatically on bot startup.
* #### handle_retry_after: A boolean flag indicating whether the mailer should handle the TelegramAPIError error automatically.
* #### destroy_on_complete: A boolean flag indicating whether the mailer should be destroyed automatically upon completing its operations.
* #### preserve: A boolean flag indicating whether the mailer's state should be preserved even after completion. If set to True, the mailer's state will be stored in the specified storage.

#### Usage:

```python
from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.mailer import DefaultMailerSettings

default = DefaultMailerSettings(
    interval=60_000,
    dynamic_interval=True,
    run_on_startup=True,
    handle_retry_after=True,
    destroy_on_complete=True,
    preserve=True,
)
broadcaster = Broadcaster(default=default)
```
