from telegram import Update
from telegram.ext import CallbackContext, Dispatcher
from telegram.ext import Filters, MessageHandler


def random_command(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда.")


def random_message(update: Update, context: CallbackContext):
    update.message.reply_text("Я не понимаю вас.")


def register(dp: Dispatcher):
    dp.add_handler(MessageHandler(Filters.command, random_command))
    dp.add_handler(MessageHandler(Filters.all, random_message))
