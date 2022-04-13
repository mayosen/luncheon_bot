from typing import List

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, Filters, CommandHandler
from telegram.ext import MessageHandler

from database.models import Product, User
from filters import is_admin


def get_photo(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=f"file_id: <code>{update.message.photo[-1].file_id}</code>",
    )


def get_products(update: Update, context: CallbackContext):
    products: List[Product] = Product.select().where(Product.category == "main_dish")
    for item in products:
        text = (
            f"{item.title}\n"
            f"Цена: {item.price}"
        )
        update.message.reply_photo(
            photo=item.photo,
            caption=text,
        )


def send_friends(update: Update, context: CallbackContext):
    friends: List[User] = User.select()
    bot = context.bot
    for friend in friends:
        update.message.reply_text(
            f"Сообщение для пользователя @{friend.username if friend.username else friend.id} "
            f"отправлено."
        )


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("products", get_products, filters=is_admin))
    dp.add_handler(CommandHandler("friends", send_friends, filters=is_admin))
    dp.add_handler(MessageHandler(Filters.photo & is_admin, get_photo))
