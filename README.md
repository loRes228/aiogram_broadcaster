# aiogram_broadcaster

![GitHub License](https://img.shields.io/github/license/loRes228/aiogram_broadcaster?style=plastic&logo=github&link=https%3A%2F%2Fgithub.com%2FloRes228%2Faiogram_broadcaster%3Ftab%3DMIT-1-ov-file)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/loRes228/aiogram_broadcaster/tests.yml?style=plastic&logo=github&link=https%3A%2F%2Fgithub.com%2FloRes228%2Faiogram_broadcaster%2Factions%2Fworkflows%2Ftests.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/loRes228/aiogram_broadcaster?style=plastic&logo=github)
![Static Badge](https://img.shields.io/badge/python-3.8%2B-blue?style=plastic&logo=python&logoColor=blue&link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)
![Static Badge](https://img.shields.io/badge/aiogram-3.4%2B-blue?style=plastic&logoColor=blue&link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)

### **aiogram_broadcaster** is lightweight aiogram-based library for broadcasting Telegram messages.

## Installation

```commandline
$ pip install git+https://github.com/loRes228/aiogram_broadcaster.git
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
from aiogram_broadcaster.storage.file import FileMailerStorage

TOKEN = "1234:Abc"  # noqa: S105
USER_IDS = {78238238, 78378343, 98765431, 12345678}  # Your user IDs list

router = Router(name=__name__)


@router.message()
async def process_any_message(message: Message, broadcaster: Broadcaster, bot: Bot) -> Any:
    # Creating content based on the Message
    content = MessageSendContent(message=message)

    mailer = await broadcaster.create_mailer(
        content=content,
        chats=USER_IDS,
        bot=bot,
        interval=1,
        preserve=True,
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
* #### status: Current [status](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/status.py) of the mailer (e.g., STARTED, STOPPED, COMPLETED).
* #### settings: Configuration settings for the mailer.
* #### statistic: [MailerStatistic](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/mailer/statistic.py) instance containing statistics about the mailer's performance.
* #### content: Content to be broadcasted.
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
broadcaster.event.include(event)
```

## Placeholders for dynamic content insertion

#### Placeholders facilitate the insertion of dynamic content within texts, this feature allows for personalized messaging.

> **_NOTE:_** `PlaceholderRouter` supports chained nesting, similar to
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

## Lazy content

#### Allows content to be generated dynamically at the time the message is sent. For example, you can customize different content for administrators and regular users.

#### Usage:

```python
from aiogram_broadcaster.contents import LazyContent, TextContent


class TimeSensitiveContent(LazyContent):
    async def __call__(self) -> TextContent:
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return TextContent(text="Good morning!")
        if 12 <= hour < 18:
            return TextContent(text="Good afternoon!")
        if 18 <= hour < 24:
            return TextContent(text="Good evening!")
        return TextContent(text="Good night!")


await broadcaster.create_mailer(content=TimeSensitiveContent(), chats=...)
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

* #### Event-to-Event

```python
@event.completed()
async def transfer_content(mailer: Mailer) -> Dict[str, Any]:
    return {"mailer_content": mailer.content}


@event.completed()
async def mailer_completed(mailer_content: BaseContent) -> None:
    print(mailer_content)
```

## Storages

#### Stores allow you to save mailer states to external storage.

* #### [FileMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storage/file.py) Saves the mailers to a file.
* #### [MongoDBMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storage/mongodb.py) Saves the mailers to a MongoDB.
* #### [RedisMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storage/redis.py) Saves the mailers to a Redis.
* #### [SQLAlchemyMailerStorage](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/storage/sqlalchemy.py) Saves the mailers using SQLAlchemy.

#### Usage:

```python
from aiogram_broadcaster import Broadcaster
from aiogram_broadcaster.storage.redis import RedisMailerStorage

# from aiogram_broadcaster.storage.file import FileMailerStorage
# from aiogram_broadcaster.storage.mongodb import MongoDBMailerStorage
# from aiogram_broadcaster.storage.sqlalchemy import SQLAlchemyMailerStorage

# storage = FileMailerStorage()
# storage = MongoDBMailerStorage.from_url(url="mongodb://localhost:27017")
# storage = SQLAlchemyMailerStorage.from_url(url="sqlite+aiosqlite:///database.db")

storage = RedisMailerStorage.from_url(url="redis://localhost:6379")
broadcaster = Broadcaster(storage=storage)
```

## Default properties

#### The [DefaultMailerProperties](https://github.com/loRes228/aiogram_broadcaster/blob/main/aiogram_broadcaster/default_properties.py) class defines the default properties for mailers created within the broadcaster. It allows setting various parameters like interval, dynamic_interval, run_on_startup, handle_retry_after, destroy_on_complete, and preserve. These properties provide flexibility and control over the behavior of mailers.

#### Parameters:

* #### interval: The interval (in seconds) between successive message broadcasts. It defaults to 0, indicating immediate broadcasting.
* #### dynamic_interval: A boolean flag indicating whether the interval should be adjusted dynamically based on the number of chats. If set to True, the interval will be divided equally among the chats.
* #### run_on_startup: A boolean flag indicating whether the mailer should start broadcasting messages automatically on bot startup.
* #### handle_retry_after: A boolean flag indicating whether the mailer should handle the TelegramAPIError error automatically.
* #### destroy_on_complete: A boolean flag indicating whether the mailer should be destroyed automatically upon completing its operations.
* #### preserve: A boolean flag indicating whether the mailer's state should be preserved even after completion. If set to True, the mailer's state will be stored in the specified storage.

#### Usage:

```python
from aiogram_broadcaster import Broadcaster, DefaultMailerProperties

default = DefaultMailerProperties(
    interval=60_000,
    dynamic_interval=True,
    run_on_startup=True,
    handle_retry_after=True,
    destroy_on_complete=True,
    preserve=True,
)
broadcaster = Broadcaster(default=default)
```
