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
    catalog, main, login, order
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


catalog_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Text(Strings.order+Strings.continue_shopping), main.order),
        MessageHandler(filters.Regex(r"^fast_order"), main.fast_order)
        ],
    states={
        GET_CAR_BRAND: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text &
                           ~filters.Text(Strings.cart) & ~filters.Text(Strings.back), catalog.get_car_brand),
        ],
        GET_PRODUCT_TYPE: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), catalog.get_product_type),
            MessageHandler(filters.Text(Strings.back),
                           catalog._to_the_getting_car_brand)
        ],
        GET_PRODUCT_SIZE: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), catalog.get_product_size),
            CallbackQueryHandler(catalog._to_the_getting_product_type, pattern="back"),

        ],
        SHOW_PRODUCTS: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text & ~filters.Text(
                Strings.cart) & ~filters.Text(Strings.back), catalog.show_product_info),
            MessageHandler(filters.Text(Strings.back),
                           catalog._to_the_getting_product_size),
            CallbackQueryHandler(catalog._to_the_getting_product_size, pattern="back"),
            CallbackQueryHandler(catalog._to_the_getting_car_brand, pattern="continue_shopping"),
            CallbackQueryHandler(catalog.start, pattern="main_menu"),
            CallbackQueryHandler(catalog.show_cart, pattern="view_cart"),
            CallbackQueryHandler(catalog.save_to_cart, pattern='save_to_cart'),
            CallbackQueryHandler(lambda update, context: catalog.update_cart_quantity(update, context, "increase"), pattern="increase_"),
            CallbackQueryHandler(lambda update, context: catalog.update_cart_quantity(update, context, "decrease"), pattern="decrease_"),
        ],
    },
    fallbacks=[
        CommandHandler('start', catalog.start),
        MessageHandler(filters.Text(Strings.main_menu), catalog.start),
        MessageHandler(filters.Text(Strings.cart), catalog.show_cart)
    ],
    name="catalog",
    persistent=True,

)


order_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Text(Strings.confirm_order), order.confirm_order)
    ],
    states={
        GET_LOCATION: [
            MessageHandler(filters.LOCATION, order.get_location)
        ],
        GET_DELIVERY_TIME: [
            MessageHandler(filters.Text(Strings.back), order._to_the_getting_location),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_delivery_time),
        ],
        GET_PAYMENT_TYPE: [
            MessageHandler(filters.Text(Strings.back), order._to_the_getting_delivery_time),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_payment_type),

        ],
        GET_COMMENT: [
            MessageHandler(filters.Text(Strings.back), order._to_the_getting_payment_type),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_comment),

        ],
    },
    fallbacks=[
        CommandHandler('start', order.start),
        MessageHandler(filters.Text(Strings.main_menu), order.start),
    ],
    name="order",
    persistent=True
)

search_product_handler = InlineQueryHandler(catalog.inline_query_handler)
empty_cart_handler = MessageHandler(
    filters.Text(Strings.to_empty_cart) & exceptions_for_filter_text,
    main.empty_cart
)

handlers = [
    login_handler,
    catalog_handler,
    order_handler,
    search_product_handler,
    empty_cart_handler,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update),
]
