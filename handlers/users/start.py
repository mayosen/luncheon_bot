from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.ext import MessageHandler

from database.api import check_user
from database.models import User


def hello_user(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text(
        text=f"Привет, <b>{message.from_user.full_name}</b>!\n\n"
             f"Я Ланч-бот, с моей помощью ты можешь заказать доставку еды на дом.\n"
             f"Чтобы собрать новый заказ, используй команду /order",
    )


@check_user
def get_me(update: Update, context: CallbackContext):
    user = User.get(id=update.message.from_user.id)
    update.message.reply_text(
        text=str(user),
    )


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("me", get_me))
    dp.add_handler(CommandHandler("start", hello_user))
