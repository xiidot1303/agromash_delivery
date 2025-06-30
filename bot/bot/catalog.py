from bot.bot import *
from app.models import Product, Cart, CartItem, Order, OrderItem, StoreProduct
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import uuid
import re


async def _to_the_getting_car_brand(update: Update, context: CustomContext):
    if update.callback_query:
        await bot_edit_message_reply_markup(update, context, reply_markup=None)

    car_brands = await sync_to_async(list)(
        StoreProduct.objects.exclude(product__car_brand=None)
        .values_list('product__car_brand', flat=True).distinct()
    )
    # Flatten the list of car brands and get distinct values
    distinct_car_brands = list(
        set(brand for brands in car_brands for brand in brands))
    reply_markup = await build_keyboard(context, distinct_car_brands, 2, cart_button=True, back_button=False)
    await update_message_reply_text(update, context.words.select_car_brand, reply_markup=reply_markup)
    return GET_CAR_BRAND


async def _to_the_getting_product_type(update: Update, context: CustomContext):
    if update.callback_query:
        await bot_edit_message_reply_markup(update, context, reply_markup=None)
    product_types = list(dict(Product.TYPE_CHOICES).values())
    reply_markup = await build_keyboard(context, product_types, 2, cart_button=True)
    message = await update.effective_message.reply_text(context.words.select_product_type, reply_markup=reply_markup)
    context.user_data['message_to_delete'] = message.message_id
    return GET_PRODUCT_TYPE


async def _to_the_getting_product_size(update: Update, context: CustomContext):
    if update.callback_query:
        await bot_edit_message_reply_markup(update, context, reply_markup=None)
    keyboard = [
        [InlineKeyboardButton(
            context.words.search_sizes, switch_inline_query_current_chat="")],
        [InlineKeyboardButton(
            context.words.back, callback_data="back"),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message: Message = await update.effective_message.reply_text(context.words.select_product_size, reply_markup=reply_markup)
    context.user_data['inline_query'] = 'sizes'

    return GET_PRODUCT_SIZE


async def _to_the_getting_product_title(update: Update, context: CustomContext):
    keyboard = [
        [InlineKeyboardButton(
            context.words.search_products, switch_inline_query_current_chat="")],
        [InlineKeyboardButton(
            context.words.back, callback_data="back"),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['inline_query'] = 'products'
    await update.message.reply_text(context.words.select_product, reply_markup=reply_markup)
    return SHOW_PRODUCTS


async def get_car_brand(update: Update, context: CustomContext):
    context.user_data['car_brand'] = update.message.text
    return await _to_the_getting_product_type(update, context)


async def get_product_type(update: Update, context: CustomContext):
    product_type_text = update.message.text
    product_type = next(
        key for key, value in Product.TYPE_CHOICES if value == product_type_text)
    if message_id := context.user_data.get('message_to_delete', None):
        await context.bot.delete_message(update.effective_chat.id, message_id)
    context.user_data['product_type'] = product_type
    return await _to_the_getting_product_size(update, context)


async def get_product_size(update: Update, context: CustomContext):
    context.user_data['product_size'] = update.message.text
    return await _to_the_getting_product_title(update, context)


async def show_product_info(update: Update, context: CustomContext, fast_order: bool = False):
    product_pk = update.message.text.split("<>")[1]
    product = await Product.objects.aget(pk=product_pk)
    context.user_data['selected_product'] = product.id
    keyboard = [
        [InlineKeyboardButton(
            context.words.add_to_cart, callback_data='save_to_cart')],
        [
            InlineKeyboardButton(
            context.words.back, callback_data="back") if not fast_order else InlineKeyboardButton(
                context.words.main_menu, callback_data='main_menu')
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if product.photo:
        await update.message.reply_photo(photo=product.photo, caption=f"<b>{product.title}</b>\n{context.words.price}: {product.price}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"<b>{product.title}</b>\n{context.words.price}: {product.price}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return


async def save_to_cart(update: Update, context: CustomContext):
    query = update.callback_query
    product_id = context.user_data['selected_product']
    product = await Product.objects.aget(id=product_id)
    user_id = update.effective_user.id
    bot_user: Bot_user = await get_object_by_user_id(user_id)
    cart, created = await Cart.objects.aget_or_create(bot_user=bot_user)
    cart_item, created = await CartItem.objects.aget_or_create(cart=cart, product=product, defaults={'quantity': 1, 'price': product.price})
    if not created:
        cart_item.quantity += 1
        await cart_item.asave()

    # Update inline buttons to "minus", "quantity", and "plus"
    keyboard = [
        [
            InlineKeyboardButton(
                "-", callback_data=f"decrease_{cart_item.id}"),
            InlineKeyboardButton(f"{cart_item.quantity}",
                                 callback_data="quantity_display"),
            InlineKeyboardButton("+", callback_data=f"increase_{cart_item.id}")
        ],
        [
            InlineKeyboardButton(
                context.words.continue_shopping, callback_data='continue_shopping'),
        ],
        [
            InlineKeyboardButton(context.words.cart, callback_data='view_cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot_edit_message_reply_markup(update, context, reply_markup=reply_markup)


async def update_cart_quantity(update: Update, context: CustomContext, action: str):
    query = update.callback_query
    cart_item_id = int(query.data.split("_")[1])
    cart_item = await CartItem.objects.aget(id=cart_item_id)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif cart_item.quantity <= 1:
        keyboard = [
            [InlineKeyboardButton(
                context.words.add_to_cart, callback_data='save_to_cart')],
            [InlineKeyboardButton(
                context.words.back, callback_data="back"),],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot_edit_message_reply_markup(update, context, reply_markup=reply_markup)
        await cart_item.adelete()
        return


    await cart_item.asave()

    # Update the inline buttons with the new quantity
    keyboard = [
        [
            InlineKeyboardButton(
                "-", callback_data=f"decrease_{cart_item.id}"),
            InlineKeyboardButton(f"{cart_item.quantity}",
                                 callback_data="quantity_display"),
            InlineKeyboardButton("+", callback_data=f"increase_{cart_item.id}")
        ],
        [
            InlineKeyboardButton(
                context.words.continue_shopping, callback_data='continue_shopping'),
        ],
        [
            InlineKeyboardButton(context.words.cart, callback_data='view_cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot_edit_message_reply_markup(update, context, reply_markup=reply_markup)


async def show_cart(update: Update, context: CustomContext):
    if update.callback_query:
        await bot_edit_message_reply_markup(update, context, reply_markup=None)
    user_id = update.effective_user.id
    bot_user: Bot_user = await get_object_by_user_id(user_id)
    cart, created = await Cart.objects.aget_or_create(bot_user=bot_user)
    if not await CartItem.objects.filter(cart=cart).aexists():
        await update.effective_message.reply_text(context.words.cart_empty)
        return

    # Generate cart text with index and quantity, and calculate overall price
    overall_price = 0
    cart_text = ""
    for index, item in await sync_to_async(enumerate)(CartItem.objects.filter(cart=cart), start=1):
        product = await item.get_product
        cart_text += f"{index}. <b>{product.title}</b>\n    {item.quantity} x {item.price} = {item.quantity * item.price}\n\n"
        overall_price += item.quantity * item.price

    cart_text += f"\n<b>{context.words.total_price}: {overall_price}</b>"
    keyboard = [
        context.words.confirm_order,
        context.words.to_empty_cart, 
        context.words.continue_shopping
    ]
    markup = await build_keyboard(context, keyboard, 1, back_button=False, main_menu_button=False)
    await update.effective_message.reply_text(cart_text, reply_markup=markup, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def start(update: Update, context: CustomContext):
    if update.callback_query:
        await bot_edit_message_reply_markup(update, context, reply_markup=None)
    await main_menu(update, context)
    return ConversationHandler.END


async def inline_query_handler(update: Update, context: CustomContext):
    query = update.inline_query.query
    query_type = context.user_data.get('inline_query')
    if query_type == 'sizes':
        sizes = await sync_to_async(list)(
            StoreProduct.objects.filter(
                product__car_brand__contains=[context.user_data['car_brand']],
                product__type=context.user_data['product_type'],
                quantity__gt=0,
                product__size__icontains=query
            ).values_list('product__size', flat=True).distinct()
        )
        results = [
            InlineQueryResultArticle(
                id=uuid.uuid4(),
                title=size,
                input_message_content=InputTextMessageContent(size)
            )
            for size in sizes
        ]
    elif query_type == 'products':
        car_brand = context.user_data.get('car_brand')
        product_type = context.user_data.get('product_type')
        product_size = context.user_data.get('product_size')

        products_ids = await sync_to_async(list)(
            StoreProduct.objects.filter(
                product__car_brand__contains=[car_brand],
                product__type=product_type,
                product__size=product_size,
                product__title__icontains=query,
                quantity__gt=0
            ).values_list('pk', flat=True)
        )
        results = [
            InlineQueryResultArticle(
                id=str(product.bitrix_id),
                title=product.title,
                input_message_content=InputTextMessageContent(
                    f"{product.title}<>{product.pk}"
                ),
                description=f"{product.price}"
            )
            async for product in Product.objects.filter(storeproduct__pk__in=products_ids).distinct()
        ]
    elif query_type == 'fast_order':
        pattern = r"\D{1}".join(query.split())
        products_ids = await sync_to_async(list)(
            StoreProduct.objects.filter(
                product__title__iregex=pattern,
                quantity__gt=0
            ).values_list('pk', flat=True)
        )
        if len(query) < 3:
            results = [
                InlineQueryResultArticle(
                    id=uuid.uuid4(),
                    title=context.words.enter_at_least_3_characters,
                    input_message_content=InputTextMessageContent("Please enter at least 3 characters")
                )
            ]
        elif not products_ids:
            results = [
                InlineQueryResultArticle(
                    id=uuid.uuid4(),
                    title=context.words.no_products_found,
                    input_message_content=InputTextMessageContent("No products found")
                )
            ]
        else:
            results = [
                InlineQueryResultArticle(
                    id=str(product.bitrix_id),
                    title=product.title,
                    input_message_content=InputTextMessageContent(
                        f"fast_order {product.title}<>{product.pk}"
                    ),
                    description=f"{product.get_type_display()} x {product.price}"
                )
                async for product in Product.objects.filter(storeproduct__pk__in=products_ids).distinct()
            ]
    await update.inline_query.answer(results, cache_time=0, auto_pagination=True)
