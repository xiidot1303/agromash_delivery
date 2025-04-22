from bot.bot import *
from app.models import Product, Cart, CartItem, Order, OrderItem
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import requests
from app.utils import send_request


async def _to_the_getting_location(update: Update, context: CustomContext):
    location_button = KeyboardButton(
        text=context.words.send_location, request_location=True)
    reply_markup = ReplyKeyboardMarkup([[location_button], [
                                       context.words.main_menu]], resize_keyboard=True, one_time_keyboard=True)
    await update.effective_message.reply_text(context.words.get_location, reply_markup=reply_markup)
    return GET_LOCATION


async def _to_the_getting_delivery_time(update: Update, context: CustomContext):
    markup = await build_keyboard(context, [], 2)
    await update.effective_message.reply_text(context.words.get_delivery_time, reply_markup=markup)
    return GET_DELIVERY_TIME


async def _to_the_getting_payment_type(update: Update, context: CustomContext):
    reply_markup = await build_keyboard(context, context.words.payment_types, 1)
    await update.effective_message.reply_text(context.words.get_payment_type, reply_markup=reply_markup)
    return GET_PAYMENT_TYPE


async def _to_the_getting_comment(update: Update, context: CustomContext):
    reply_markup = await build_keyboard(context, [], 1)
    await update.effective_message.reply_text(context.words.get_comment, reply_markup=reply_markup)
    return GET_COMMENT

#########################################################################################

async def confirm_order(update: Update, context: CustomContext):
    return await _to_the_getting_location(update, context)


async def get_location(update: Update, context: CustomContext):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    context.user_data['location'] = f"{latitude}, {longitude}"
    # Fetch address from coordinates using a geocoding API
    try:
        response = await send_request(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json")
        address = response.get("display_name", "Unknown address")
        context.user_data['address'] = address
    except:
        context.user_data['address'] = "Unknown address"
    return await _to_the_getting_delivery_time(update, context)


async def get_delivery_time(update: Update, context: CustomContext):
    context.user_data['delivery_time'] = update.effective_message.text
    return await _to_the_getting_payment_type(update, context)


async def get_payment_type(update: Update, context: CustomContext):
    context.user_data['payment_type'] = update.effective_message.text
    return await _to_the_getting_comment(update, context)


async def get_comment(update: Update, context: CustomContext):
    context.user_data['comment'] = update.effective_message.text
    return await place_order(update, context)


async def place_order(update: Update, context: CustomContext):
    user_id = update.effective_user.id
    bot_user: Bot_user = await get_object_by_user_id(user_id)
    cart = await Cart.objects.aget(bot_user=bot_user)
    cart_items = await sync_to_async(list)(CartItem.objects.filter(cart=cart))
    order = await Order.objects.acreate(
        bot_user=bot_user,
        customer_name=bot_user.name,
        customer_phone=bot_user.phone,
        customer_email="",
        customer_address=context.user_data['address'],  # Use the fetched address
        delivery_time=context.user_data['delivery_time'],
        location=context.user_data['location'],
        payment_type=context.user_data['payment_type'],
        status='pending'
    )
    for item in cart_items:
        await OrderItem.objects.acreate(order=order, product=await item.get_product, quantity=item.quantity, price=item.price)
    await CartItem.objects.filter(cart=cart).adelete()
    await update.effective_message.reply_text(context.words.your_order_accepted)
    await main_menu(update, context)
    return ConversationHandler.END


async def start(update: Update, context: CustomContext):
    await main_menu(update, context)
    return ConversationHandler.END
