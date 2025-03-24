from dataclasses import dataclass
from typing import Optional
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
    PicklePersistence
)
from telegram import (
    ReplyKeyboardMarkup
)
from bot.resources.strings import Strings


@dataclass
class NewsletterUpdate:
    user_id: int
    text: str
    photo: Optional[object | str] = None
    video: Optional[object | str] = None
    document: Optional[object] = None
    reply_markup: Optional[ReplyKeyboardMarkup] = None
    pin_message: bool = False


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.words = Strings(self._user_id)

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, NewsletterUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)
