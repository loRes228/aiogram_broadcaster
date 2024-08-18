from typing import Any, NamedTuple, Optional

from aiogram.methods import (
    CopyMessage,
    CopyMessages,
    ForwardMessage,
    ForwardMessages,
    SendAnimation,
    SendAudio,
    SendChatAction,
    SendContact,
    SendDice,
    SendDocument,
    SendGame,
    SendInvoice,
    SendLocation,
    SendMediaGroup,
    SendMessage,
    SendPaidMedia,
    SendPhoto,
    SendPoll,
    SendSticker,
    SendVenue,
    SendVideo,
    SendVideoNote,
    SendVoice,
)
from aiogram.types import Message

from .parser import FieldNode


class Target(NamedTuple):
    method: Any
    content_name: str
    content_file_name: str
    call_result: str
    method_exec: str
    put_model_extra: bool = True
    model_extra_nodes: Optional[list[FieldNode]] = None


TARGETS = (
    Target(
        method=CopyMessage,
        content_name="FromChatCopyMessageContent",
        content_file_name="from_chat_copy_message",
        call_result="CopyMessage",
        method_exec="CopyMessage",
    ),
    Target(
        method=CopyMessages,
        content_name="FromChatCopyMessagesContent",
        content_file_name="from_chat_copy_messages",
        call_result="CopyMessages",
        method_exec="CopyMessages",
    ),
    Target(
        method=ForwardMessage,
        content_name="FromChatForwardMessageContent",
        content_file_name="from_chat_forward_message",
        call_result="ForwardMessage",
        method_exec="ForwardMessage",
    ),
    Target(
        method=ForwardMessages,
        content_name="FromChatForwardMessagesContent",
        content_file_name="from_chat_forward_messages",
        call_result="ForwardMessages",
        method_exec="ForwardMessages",
    ),
    Target(
        method=SendAnimation,
        content_name="AnimationContent",
        content_file_name="animation",
        call_result="SendAnimation",
        method_exec="SendAnimation",
    ),
    Target(
        method=SendAudio,
        content_name="AudioContent",
        content_file_name="audio",
        call_result="SendAudio",
        method_exec="SendAudio",
    ),
    Target(
        method=SendChatAction,
        content_name="ChatActionContent",
        content_file_name="chat_action",
        call_result="SendChatAction",
        method_exec="SendChatAction",
    ),
    Target(
        method=SendContact,
        content_name="ContactContent",
        content_file_name="contact",
        call_result="SendContact",
        method_exec="SendContact",
    ),
    Target(
        method=SendDice,
        content_name="DiceContent",
        content_file_name="dice",
        call_result="SendDice",
        method_exec="SendDice",
    ),
    Target(
        method=SendDocument,
        content_name="DocumentContent",
        content_file_name="document",
        call_result="SendDocument",
        method_exec="SendDocument",
    ),
    Target(
        method=SendGame,
        content_name="GameContent",
        content_file_name="game",
        call_result="SendGame",
        method_exec="SendGame",
    ),
    Target(
        method=SendInvoice,
        content_name="InvoiceContent",
        content_file_name="invoice",
        call_result="SendInvoice",
        method_exec="SendInvoice",
    ),
    Target(
        method=SendLocation,
        content_name="LocationContent",
        content_file_name="location",
        call_result="SendLocation",
        method_exec="SendLocation",
    ),
    Target(
        method=SendMediaGroup,
        content_name="MediaGroupContent",
        content_file_name="media_group",
        call_result="SendMediaGroup",
        method_exec="SendMediaGroup",
    ),
    Target(
        method=SendMessage,
        content_name="TextContent",
        content_file_name="text",
        call_result="SendMessage",
        method_exec="SendMessage",
    ),
    Target(
        method=SendPaidMedia,
        content_name="PaidMediaContent",
        content_file_name="paid_media",
        call_result="SendPaidMedia",
        method_exec="SendPaidMedia",
    ),
    Target(
        method=SendPhoto,
        content_name="PhotoContent",
        content_file_name="photo",
        call_result="SendPhoto",
        method_exec="SendPhoto",
    ),
    Target(
        method=SendPoll,
        content_name="PollContent",
        content_file_name="poll",
        call_result="SendPoll",
        method_exec="SendPoll",
    ),
    Target(
        method=SendSticker,
        content_name="StickerContent",
        content_file_name="sticker",
        call_result="SendSticker",
        method_exec="SendSticker",
    ),
    Target(
        method=SendVenue,
        content_name="VenueContent",
        content_file_name="venue",
        call_result="SendVenue",
        method_exec="SendVenue",
    ),
    Target(
        method=SendVideo,
        content_name="VideoContent",
        content_file_name="video",
        call_result="SendVideo",
        method_exec="SendVideo",
    ),
    Target(
        method=SendVideoNote,
        content_name="VideoNoteContent",
        content_file_name="video_note",
        call_result="SendVideoNote",
        method_exec="SendVideoNote",
    ),
    Target(
        method=SendVoice,
        content_name="VoiceContent",
        content_file_name="voice",
        call_result="SendVoice",
        method_exec="SendVoice",
    ),
    Target(
        method=Message.send_copy,
        content_name="MessageSendContent",
        content_file_name="message_send",
        call_result="Union[ForwardMessage, SendAnimation, SendAudio, SendContact, SendDocument, SendLocation, SendMessage, SendPhoto, SendPoll, SendDice, SendSticker, SendVenue, SendVideo, SendVideoNote, SendVoice]",
        method_exec="self.message.send_copy",
        put_model_extra=False,
        model_extra_nodes=[FieldNode(name="message", annotation="Message")],
    ),
    Target(
        method=Message.forward,
        content_name="MessageForwardContent",
        content_file_name="message_forward",
        call_result="ForwardMessage",
        method_exec="self.message.forward",
        model_extra_nodes=[FieldNode(name="message", annotation="Message")],
    ),
    Target(
        method=Message.copy_to,
        content_name="MessageCopyContent",
        content_file_name="message_copy",
        call_result="CopyMessage",
        method_exec="self.message.copy_to",
        model_extra_nodes=[FieldNode(name="message", annotation="Message")],
    ),
)
