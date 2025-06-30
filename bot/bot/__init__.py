from bot import *
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext, ExtBot, Application
from dataclasses import dataclass
from asgiref.sync import sync_to_async
from bot.utils import *
from bot.utils.bot_functions import *
from bot.utils.keyboards import *
from bot.services import *
from bot.resources.conversationList import *
from app.services import filter_objects_sync
from config import WEBAPP_URL


async def is_message_back(update: Update):
    if update.message.text == Strings(update.effective_user.id).back:
        return True
    else:
        return False


async def main_menu(update: Update, context: CustomContext):
    bot = context.bot

    buttons = [
        [context.words.order]
        ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    await bot.send_message(
        update.effective_message.chat_id,
        context.words.main_menu,
        reply_markup=markup
    )

    context.user_data['inline_query'] = 'fast_order'
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(context.words.search, switch_inline_query_current_chat='')],
    ])
    await bot.send_message(
        update.effective_message.chat_id,
        context.words.search_products,
        reply_markup=markup
    )
