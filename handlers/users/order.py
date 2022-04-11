import re
from typing import List

from telegram import Update, InputMediaPhoto, MessageEntity, Message, CallbackQuery
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.api import check_user
from database.models import User, Product, Order
from keyboards.product import get_product_keyboard, phone_keyboard, address_keyboard


MAIN_DISH, SNACK, DRINK, PHONE, ADDRESS = range(5)


@check_user
def make_order(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"] = []

    products: List[Product] = Product.select().where(Product.category == "main_dish")
    context.user_data["cache"] = products

    message.reply_text("Начата сборка заказа.\n/cancel - отменить заказ")
    message.reply_text("Выберите основное блюдо.")

    index = 0
    product = products[index]

    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price}",
        reply_markup=get_product_keyboard(index, len(products)),
    )

    return MAIN_DISH


def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text("Заказ отменен. Ждем вас еще!")

    return ConversationHandler.END


def switch_product(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    new_index = int(re.match(r"index:(\d+)", query.data).groups()[0])

    products = context.user_data["cache"]
    product = products[new_index]

    query.message.edit_media(
        media=InputMediaPhoto(
            media=product.photo,
            caption=f"{product.title}\nЦена: {product.price}",
        ),
        reply_markup=get_product_keyboard(new_index, len(products)),
    )


def process_category(field: str, alias: str, query: CallbackQuery, user_data: dict):
    query.answer()
    query.edit_message_reply_markup()

    index = int(re.match(r"cart:(\d+)", query.data).groups()[0])
    products = user_data["cache"]
    user_data["cart"].append(products[index])

    products: List[Product] = Product.select().where(Product.category == field)
    user_data["cache"] = products

    index = 0
    product = products[index]

    message = query.message
    message.reply_text(f"Выберите {alias}.")
    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price}",
        reply_markup=get_product_keyboard(index, len(products)),
    )


def get_main_dish(update: Update, context: CallbackContext):
    process_category("snack", "закуску", update.callback_query, context.user_data)

    return SNACK


def get_snack(update: Update, context: CallbackContext):
    process_category("drink", "напиток", update.callback_query, context.user_data)

    return DRINK


def get_drink(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    index = int(re.match(r"cart:(\d+)", query.data).groups()[0])

    user_data = context.user_data
    products = user_data["cache"]
    user_data["cart"].append(products[index])
    del user_data["cache"]

    message = query.message
    message.edit_reply_markup()
    message.reply_text("Корзина сформирована.")

    user = User.get(id=query.from_user.id)

    if user.phone:
        message.reply_text(
            text=f"В прошлом заказе вы указывали номер:\n<code>{user.phone}</code>\n"
                 f"Использовать его в в этом заказе?",
            reply_markup=phone_keyboard,
        )
    else:
        message.reply_text("Введите ваш номер телефона или отправьте контакт.")

    return PHONE


def incorrect_phone(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Пожалуйста, введите корректный номер телефона. \n"
        "Он нужен, чтобы связаться с вами в случае возникновения затруднений.")


def enter_new_phone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    query.message.reply_text("Введите новый номер телефона или отправьте контакт.")

    user = User.get(id=query.from_user.id)
    user.phone = ""
    user.save()


def use_last_phone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()

    user = User.get(id=query.from_user.id)

    return to_address(query.message, user)


def get_phone(update: Update, context: CallbackContext):
    message = update.message
    phone = message.contact.phone_number if message.contact else message.text

    user = User.get(id=message.from_user.id)
    user.phone = phone
    user.save()

    return to_address(message, user)


def to_address(message: Message, user: User):
    if user.address:
        message.reply_text(
            text=f"В прошлом заказе вы указывали адрес:\n<code>{user.address}</code>\n"
                 f"Использовать его в в этом заказе?",
            reply_markup=address_keyboard,
        )
    else:
        message.reply_text("Введите адрес доставки или пришлите локацию.")

    return ADDRESS


def enter_new_address(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    query.message.reply_text("Введите новый адрес или отправьте локацию.")

    user = User.get(id=query.from_user.id)
    user.address = ""
    user.save()


def use_last_address(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    user = User.get(id=query.from_user.id)

    return create_order(query.message, user, context.user_data)


def get_address(update: Update, context: CallbackContext):
    message = update.message

    if message.location:
        address = f"{message.location.latitude} {message.location.longitude}"
    else:
        address = message.text

    user = User.get(id=message.from_user.id)
    user.address = address
    user.save()

    return create_order(message, user, context.user_data)


def create_order(message: Message, user: User, user_data: dict):
    # TODO: Создание заказа
    # Писать его номер.
    # Тут надо уведомлять админов

    message.reply_text(f"Спасибо! Ваш заказ по адресу\n<code>{user.address}</code>\nпринят в обработку.")
    user_data.clear()

    return ConversationHandler.END


def register(dp: Dispatcher):
    order = ConversationHandler(
        entry_points=[
            CommandHandler("order", make_order),
            MessageHandler(Filters.regex(re.compile(r".*(новый|заказ).*", re.IGNORECASE)), make_order),
        ],
        states={
            MAIN_DISH: [
                CallbackQueryHandler(pattern=r"^index:", callback=switch_product),
                CallbackQueryHandler(pattern=r"^cart:", callback=get_main_dish),
            ],
            SNACK: [
                CallbackQueryHandler(pattern=r"^index:", callback=switch_product),
                CallbackQueryHandler(pattern=r"^cart:", callback=get_snack),
            ],
            DRINK: [
                CallbackQueryHandler(pattern=r"^index:", callback=switch_product),
                CallbackQueryHandler(pattern=r"^cart:", callback=get_drink),
            ],
            PHONE: [
                MessageHandler(Filters.entity(MessageEntity.PHONE_NUMBER) | Filters.contact, get_phone),
                CallbackQueryHandler(pattern=r"^last_phone?", callback=use_last_phone),
                CallbackQueryHandler(pattern=r"^new_phone?", callback=enter_new_phone),
                MessageHandler(Filters.text & ~Filters.command, incorrect_phone),
            ],
            ADDRESS: [
                MessageHandler((Filters.text & ~Filters.command) | Filters.location, get_address),
                CallbackQueryHandler(pattern=r"^last_address?", callback=use_last_address),
                CallbackQueryHandler(pattern=r"^new_address?", callback=enter_new_address),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(Filters.regex(re.compile(r".*(отмена|стоп).*", re.IGNORECASE)), cancel),
        ],
    )

    dp.add_handler(order)
