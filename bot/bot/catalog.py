from bot.bot import *
from app.models import Product, Cart, CartItem, Order, OrderItem
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def _to_the_getting_car_brand(update: Update, context: CustomContext):
    car_brands = await sync_to_async(list)(Product.objects.values_list('car_brand', flat=True).distinct())
    reply_markup = await build_keyboard(context, car_brands, 2, cart_button=True, back_button=False)
    await update_message_reply_text(update, context.words.select_car_brand, reply_markup=reply_markup)
    return GET_CAR_BRAND


async def _to_the_getting_product_type(update: Update, context: CustomContext):
    product_types = list(dict(Product.TYPE_CHOICES).values())
    reply_markup = await build_keyboard(context, product_types, 2, cart_button=True)
    await update.message.reply_text(context.words.select_product_type, reply_markup=reply_markup)
    return GET_PRODUCT_TYPE


async def _to_the_getting_product_size(update: Update, context: CustomContext):
    sizes = await sync_to_async(list)(Product.objects.filter(car_brand=context.user_data['car_brand'], type=context.user_data['product_type']).values_list('size', flat=True).distinct())
    reply_markup = await build_keyboard(context, sizes, 2, cart_button=True)
    await update.message.reply_text(context.words.select_product_size, reply_markup=reply_markup)
    return GET_PRODUCT_SIZE


async def _to_the_getting_product_title(update: Update, context: CustomContext):
    products = await sync_to_async(list)(Product.objects.filter(car_brand=context.user_data['car_brand'], type=context.user_data['product_type'], size=context.user_data['product_size']))
    product_titles = [
        f"{product.title} - {product.price}" for product in products]
    reply_markup = await build_keyboard(context, product_titles, 2, cart_button=True)
    await update.message.reply_text(context.words.select_product, reply_markup=reply_markup)
    return SHOW_PRODUCTS


async def get_car_brand(update: Update, context: CustomContext):
    context.user_data['car_brand'] = update.message.text
    return await _to_the_getting_product_type(update, context)


async def get_product_type(update: Update, context: CustomContext):
    product_type_text = update.message.text
    product_type = next(
        key for key, value in Product.TYPE_CHOICES if value == product_type_text)
    context.user_data['product_type'] = product_type
    return await _to_the_getting_product_size(update, context)


async def get_product_size(update: Update, context: CustomContext):
    context.user_data['product_size'] = update.message.text
    return await _to_the_getting_product_title(update, context)


async def show_product_info(update: Update, context: CustomContext):
    product_title = update.message.text.split(" - ")[0]
    product = await sync_to_async(Product.objects.get)(title=product_title, car_brand=context.user_data['car_brand'], type=context.user_data['product_type'], size=context.user_data['product_size'])
    context.user_data['selected_product'] = product.id
    keyboard = [[InlineKeyboardButton(
        context.words.add_to_cart, callback_data='save_to_cart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if product.photo:
        await update.message.reply_photo(photo=product.photo, caption=f"<b>{product.title}</b>\n{context.words.price}: {product.price}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"{product.title}\nPrice: {context.words.price}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return


async def save_to_cart(update: Update, context: CustomContext):
    query = update.callback_query
    product_id = context.user_data['selected_product']
    product = await Product.objects.aget(id=product_id)
    await query.answer(f"{product.title} {context.words.added_to_cart}", show_alert=True)
    user_id = update.effective_user.id
    bot_user: Bot_user = await get_object_by_user_id(user_id)
    cart, created = await Cart.objects.aget_or_create(bot_user=bot_user)
    cart_item, created = await CartItem.objects.aget_or_create(cart=cart, product=product, defaults={'quantity': 1, 'price': product.price})
    if not created:
        cart_item.quantity += 1
        await cart_item.asave()
    await bot_edit_message_reply_markup(update, context)
    return await _to_the_getting_car_brand(update, context)


async def show_cart(update: Update, context: CustomContext):
    user_id = update.effective_user.id
    bot_user: Bot_user = await get_object_by_user_id(user_id)
    cart = await Cart.objects.aget(bot_user=bot_user)
    if not await CartItem.objects.filter(cart=cart).aexists():
        await update.message.reply_text("Your cart is empty.")
        return
    cart_text = "\n".join([f"<b>{(await item.get_product).title}</b> | {(await item.get_product).size} - {item.price}"
                           async for item in CartItem.objects.filter(cart=cart)
                           ])
    keyboard = [[InlineKeyboardButton(
        context.words.confirm_order, callback_data='confirm_order')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(cart_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def start(update: Update, context: CustomContext):
    await main_menu(update, context)
    return ConversationHandler.END
