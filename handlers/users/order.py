import re
from typing import List

from telegram import Update, InputMediaPhoto, MessageEntity
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.api import check_user
from database.models import Product, Order, User
from keyboards.product import product_keyboard


MAIN_DISH, SNACK, DRINK, ADDRESS, PHONE = range(5)


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
        reply_markup=product_keyboard(index, len(products)),
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
        reply_markup=product_keyboard(new_index, len(products)),
    )


def get_main_dish(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    index = int(re.match(r"cart:(\d+)", query.data).groups()[0])

    user_data = context.user_data
    products = user_data["cache"]
    user_data["cart"].append(products[index])
    user_data["cache"] = []

    query.message.edit_reply_markup()

    message = query.message
    products: List[Product] = Product.select().where(Product.category == "snack")
    context.user_data["cache"] = products

    index = 0
    product = products[index]

    message.reply_text("Выберите закуску.")
    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price}",
        reply_markup=product_keyboard(index, len(products)),
    )

    return SNACK


def get_snack(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    index = int(re.match(r"cart:(\d+)", query.data).groups()[0])

    user_data = context.user_data
    products = user_data["cache"]
    user_data["cart"].append(products[index])
    user_data["cache"] = []

    query.message.edit_reply_markup()

    message = query.message
    products: List[Product] = Product.select().where(Product.category == "drink")
    context.user_data["cache"] = products

    index = 0
    product = products[index]

    message.reply_text("Выберите напиток.")
    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price}",
        reply_markup=product_keyboard(index, len(products)),
    )

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
    message.reply_text("Корзина сформирована.\n\nВведите ваш номер телефона.")

    return PHONE


def get_phone(update: Update, context: CallbackContext):
    message = update.message
    user = User.get(id=message.from_user.id)

    phone = message.text

    # TODO: Использовать телефон из базы или ввести новый

    message.reply_text("Введите адрес доставки или пришлите локацию.")

    return ADDRESS


def incorrect_phone(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Пожалуйста, введите корректный номер телефона. \n"
        "Он нужен, чтобы связаться с вами в случае возникновения затруднений.")


def get_address(update: Update, context: CallbackContext):
    message = update.message

    if message.location:
        address = f"{message.location.latitude} {message.location.longitude}"
    else:
        address = message.text

    # TODO: Создание заказа

    context.user_data.clear()
    message.reply_text(f"Спасибо! Ваш заказ по адресу <code>{address}</code> принят в обработку.")

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
                MessageHandler(Filters.entity(MessageEntity.PHONE_NUMBER), get_phone),
                MessageHandler(Filters.text, incorrect_phone),
            ],
            ADDRESS: [
                MessageHandler(Filters.text | Filters.location, get_address),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(Filters.regex(re.compile(r".*(отмена|стоп).*", re.IGNORECASE)), cancel),
        ],
    )

    dp.add_handler(order)
