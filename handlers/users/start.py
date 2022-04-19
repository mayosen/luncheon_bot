from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler


def hello_user(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text(
        text=f"Привет, <b>{message.from_user.full_name}</b>!\n\n"
             f"Я Ланч-бот, с моей помощью ты можешь заказать доставку еды на дом.\n\n"
             f"Чтобы сделать заказ, используй команду /order",
    )


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("start", hello_user))
