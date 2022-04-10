from typing import List

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.ext import MessageHandler

from filters import is_admin

from database.models import Product


def admin_echo(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=update.message.text,
    )


def get_products(update: Update, context: CallbackContext):

    products: List[Product] = Product.select().where(Product.category == "main_dish")
    for item in products:
        update.message.reply_photo(
            photo=item.photo,
            caption=item.title,
        )


def register(dp: Dispatcher):
    # dp.add_handler(MessageHandler(is_admin, admin_echo))
    pass
    dp.add_handler(CommandHandler("products", get_products, filters=is_admin))
