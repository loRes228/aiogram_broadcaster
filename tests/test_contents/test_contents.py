import pytest
from aiogram.methods.base import TelegramMethod
from aiogram.methods.copy_message import CopyMessage
from aiogram.methods.forward_message import ForwardMessage
from aiogram.methods.send_animation import SendAnimation
from aiogram.methods.send_audio import SendAudio
from aiogram.methods.send_chat_action import SendChatAction
from aiogram.methods.send_contact import SendContact
from aiogram.methods.send_dice import SendDice
from aiogram.methods.send_document import SendDocument
from aiogram.methods.send_game import SendGame
from aiogram.methods.send_invoice import SendInvoice
from aiogram.methods.send_location import SendLocation
from aiogram.methods.send_media_group import SendMediaGroup
from aiogram.methods.send_message import SendMessage
from aiogram.methods.send_photo import SendPhoto
from aiogram.methods.send_poll import SendPoll
from aiogram.methods.send_sticker import SendSticker
from aiogram.methods.send_venue import SendVenue
from aiogram.methods.send_video import SendVideo
from aiogram.methods.send_video_note import SendVideoNote
from aiogram.methods.send_voice import SendVoice

from aiogram_broadcaster.contents.animation import AnimationContent
from aiogram_broadcaster.contents.audio import AudioContent
from aiogram_broadcaster.contents.chat_action import ChatActionContent
from aiogram_broadcaster.contents.contact import ContactContent
from aiogram_broadcaster.contents.dice import DiceContent
from aiogram_broadcaster.contents.document import DocumentContent
from aiogram_broadcaster.contents.from_chat import FromChatCopyContent, FromChatForwardContent
from aiogram_broadcaster.contents.game import GameContent
from aiogram_broadcaster.contents.invoice import InvoiceContent
from aiogram_broadcaster.contents.location import LocationContent
from aiogram_broadcaster.contents.media_group import MediaGroupContent
from aiogram_broadcaster.contents.message import (
    MessageCopyContent,
    MessageForwardContent,
    MessageSendContent,
)
from aiogram_broadcaster.contents.photo import PhotoContent
from aiogram_broadcaster.contents.poll import PollContent
from aiogram_broadcaster.contents.sticker import StickerContent
from aiogram_broadcaster.contents.text import TextContent
from aiogram_broadcaster.contents.venue import VenueContent
from aiogram_broadcaster.contents.video import VideoContent
from aiogram_broadcaster.contents.video_note import VideoNoteContent
from aiogram_broadcaster.contents.voice import VoiceContent


@pytest.mark.parametrize(
    ("expected_method", "content_class", "content_data"),
    [
        (
            SendAnimation,
            AnimationContent,
            {"animation": "test"},
        ),
        (
            SendAudio,
            AudioContent,
            {"audio": "test"},
        ),
        (
            SendChatAction,
            ChatActionContent,
            {"action": "test"},
        ),
        (
            SendContact,
            ContactContent,
            {"phone_number": "test", "first_name": "test"},
        ),
        (
            SendDice,
            DiceContent,
            {},
        ),
        (
            SendDocument,
            DocumentContent,
            {"document": "test"},
        ),
        (
            CopyMessage,
            FromChatCopyContent,
            {"from_chat_id": 0, "message_id": 0},
        ),
        (
            ForwardMessage,
            FromChatForwardContent,
            {"from_chat_id": 0, "message_id": 0},
        ),
        (
            SendGame,
            GameContent,
            {"game_short_name": "test"},
        ),
        (
            SendInvoice,
            InvoiceContent,
            {
                "title": "test",
                "description": "test",
                "payload": "test",
                "provider_token": "test",
                "currency": "test",
                "prices": [{"label": "test", "amount": 0}],
            },
        ),
        (
            SendLocation,
            LocationContent,
            {"latitude": 0, "longitude": 0},
        ),
        (
            SendMediaGroup,
            MediaGroupContent,
            {"media": [{"media": "test"}]},
        ),
        (
            CopyMessage,
            MessageCopyContent,
            {"message": {"message_id": 0, "date": 0, "chat": {"id": 0, "type": "test"}}},
        ),
        (
            ForwardMessage,
            MessageForwardContent,
            {"message": {"message_id": 0, "date": 0, "chat": {"id": 0, "type": "test"}}},
        ),
        (
            TelegramMethod,
            MessageSendContent,
            {
                "message": {
                    "message_id": 0,
                    "date": 0,
                    "chat": {"id": 0, "type": "test"},
                    "text": "test",
                },
            },
        ),
        (
            SendPhoto,
            PhotoContent,
            {"photo": "test"},
        ),
        (
            SendPoll,
            PollContent,
            {"question": "test", "options": ["test"]},
        ),
        (
            SendSticker,
            StickerContent,
            {"sticker": "test"},
        ),
        (
            SendMessage,
            TextContent,
            {"text": "test"},
        ),
        (
            SendVenue,
            VenueContent,
            {"latitude": 0, "longitude": 0, "title": "test", "address": "test"},
        ),
        (
            SendVideo,
            VideoContent,
            {"video": "test"},
        ),
        (
            SendVideoNote,
            VideoNoteContent,
            {"video_note": "test"},
        ),
        (
            SendVoice,
            VoiceContent,
            {"voice": "test"},
        ),
    ],
)
class TestContents:
    async def test_as_method(self, expected_method, content_class, content_data):
        content = content_class(**content_data, test_extra=1)
        result = await content.as_method(chat_id=1)
        assert isinstance(result, expected_method)
        assert result.chat_id == 1
        if content_class is MessageSendContent:
            pytest.skip(
                "MessageSendContent does not support passing extra, "
                "since the Message.send_copy method does not accept **kwargs.",
            )
        assert result.test_extra == 1
