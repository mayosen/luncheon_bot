from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.ext import Filters, MessageHandler

from utils.literals import Info


def hello_user(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text(
        text=f"Привет, <b>{message.from_user.full_name}</b>!\n\n"
             f"Я Ланч-бот, с моей помощью ты можешь заказать доставку еды на дом.\n\n"
             f"Чтобы сделать заказ, используй команду /order",
    )


def random_command(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда.\n\n" + Info.COMMANDS_HINT)


def random_message(update: Update, context: CallbackContext):
    update.message.reply_text("Я не понимаю вас.\n\n" + Info.COMMANDS_HINT)


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("start", hello_user))
    dp.add_handler(MessageHandler(Filters.command, random_command))
    dp.add_handler(MessageHandler(Filters.all, random_message))
