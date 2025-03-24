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
    main, login, order
)

exceptions_for_filter_text = (~filters.COMMAND) & (
    ~filters.Text(Strings.main_menu))

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

order_handler = ConversationHandler(
    entry_points=[CommandHandler("order", main.order)],
    states={
        GET_CAR_BRAND: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text &
                           ~filters.Text(Strings.cart) & ~filters.Text(Strings.back), order.get_car_brand),
        ],
        GET_PRODUCT_TYPE: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), order.get_product_type),
            MessageHandler(filters.Text(Strings.back),
                           order._to_the_getting_car_brand)
        ],
        GET_PRODUCT_SIZE: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), order.get_product_size),
            MessageHandler(filters.Text(Strings.back),
                           order._to_the_getting_product_type)
        ],
        SHOW_PRODUCTS: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), order.show_product_info),
            MessageHandler(filters.Text(Strings.back),
                           order._to_the_getting_product_size),
            CallbackQueryHandler(order.save_to_cart, pattern='save_to_cart'),
            CallbackQueryHandler(order.place_order, pattern='place_order')
        ],
    },
    fallbacks=[
        CommandHandler('start', order.start),
        MessageHandler(filters.Text(Strings.main_menu), order.start),
        MessageHandler(filters.Text(Strings.cart), order.show_cart)
    ],
    name="order",
    persistent=True,

)

handlers = [
    login_handler,
    order_handler,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]
