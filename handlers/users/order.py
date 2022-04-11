import re
from typing import List

from telegram import Update, InputMediaPhoto
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.models import Product
from keyboards.product import product_keyboard


MAIN_DISH, SNACK, DRINK = range(3)


def make_order(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"] = []
    products: List[Product] = Product.select().where(Product.category == "main_dish")
    context.user_data["cache"] = products

    message.reply_text("Начата сборка заказа.\nВыберите основное блюдо.")

    index = 0
    product = products[index]

    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price}",
        reply_markup=product_keyboard(index, products),
    )

    return MAIN_DISH


def switch_product(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    new_index = int(re.match(r"index:(\d+)", data).groups()[0])
    products: List[Product] = context.user_data["cache"]
    product = products[new_index]

    query.message.edit_media(
        media=InputMediaPhoto(product.photo, caption=f"{product.title}\nЦена: {product.price}"),
        reply_markup=product_keyboard(new_index, products),
    )


def add_to_cart(update: Update, context: CallbackContext):
    update.callback_query.answer()
    update.message.edit_reply_markup()
    context.user_data["cache"] = []
    # TODO: Удалять клавиатуру
    query.answer()
    update.message.reply_text("Added to cart")

    # return ?


def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text("Заказ отменен. Ждем вас еще!")
    return ConversationHandler.END


def get_main_dish(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    message.reply_text("Отлично!\nТеперь выберите закуску.")
    return SNACK


def get_snack(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    message.reply_text("Отлично!\nТеперь выберите напиток.")
    return DRINK


def get_drink(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    # TODO: Кладем в базу
    message.reply_text("Спасибо!\nВаш заказ отправлен в обработку.")
    context.user_data.clear()
    return ConversationHandler.END


def register(dp: Dispatcher):
    order = ConversationHandler(
        entry_points=[CommandHandler("order", make_order)],
        states={
            MAIN_DISH: [
                MessageHandler(Filters.text & ~Filters.command, get_main_dish),
                CallbackQueryHandler(pattern=r"^index:", callback=switch_product),
                CallbackQueryHandler(pattern=r"^cart:", callback=add_to_cart),
            ],
            SNACK: [
                MessageHandler(Filters.text & ~Filters.command, get_snack),


            ],
            DRINK: [
                MessageHandler(Filters.text & ~Filters.command, get_drink),


            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(order)
    # TODO: По окончании заказа чистить `user_data`
