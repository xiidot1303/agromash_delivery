from bot import *
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    TypeHandler,
    ConversationHandler
)

from bot.resources.conversationList import *

from bot.bot import (
    main, login
)

exceptions_for_filter_text = (~filters.COMMAND) & (~filters.Text(Strings.main_menu))

login_handler = ConversationHandler(
    entry_points=[CommandHandler("start", main.start)],
    states={
        SELECT_LANG: [MessageHandler(
            filters.Text(Strings.uz_ru) & exceptions_for_filter_text,
            login.select_lang
            )],
        GET_NAME: [MessageHandler(filters.TEXT & exceptions_for_filter_text, login.get_name)],
        GET_REGION: [MessageHandler(filters.TEXT & exceptions_for_filter_text, login.get_region)],
        GET_CONTACT: [MessageHandler(filters.ALL & exceptions_for_filter_text, login.get_contact)],
    },
    fallbacks=[
        CommandHandler('start', login.start)
    ],
    name="login",
    persistent=True,

)

handlers = [
    login_handler,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]