import re
from typing import List

from telegram import Update, InputMediaPhoto
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.api import check_user
from database.models import Product, Order
from keyboards.product import product_keyboard


MAIN_DISH, SNACK, DRINK, ADDRESS, PHONE = range(5)


@check_user
def make_order(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"] = []
    products: List[Product] = Product.select().where(Product.category == "main_dish")
    context.user_data["cache"] = products

    message.reply_text("Начата сборка заказа.\n/cancel - Отмена заказа\n\n"
                       "Выберите основное блюдо.")

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

    message.reply_text("Отлично. Теперь выберите закуску.")

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

    message.reply_text("Спасибо. Теперь выберите напиток.")

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

    user_data.clear()
    query.message.edit_reply_markup()

    message = query.message

    message.reply_text("Супер. Ваш заказ принят в обработку.")

    # TODO: Запрос на юзера и создание заказа

    return ConversationHandler.END


def get_phone():
    pass


def get_address():
    pass


def register(dp: Dispatcher):
    order = ConversationHandler(
        entry_points=[CommandHandler("order", make_order)],
        states={
            MAIN_DISH: [
                MessageHandler(Filters.text & ~Filters.command, get_main_dish),
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
            ADDRESS: [

            ],
            PHONE: [

            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(order)
