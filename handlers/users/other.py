from telegram import Update
from telegram.ext import Dispatcher, CallbackContext
from telegram.ext import Filters, MessageHandler

from utils.literals import COMMANDS_HINT


def random_command(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда.\n\n" + COMMANDS_HINT)


def random_message(update: Update, context: CallbackContext):
    update.message.reply_text("Я не понимаю вас.\n\n" + COMMANDS_HINT)


def register(dp: Dispatcher):
    dp.add_handler(MessageHandler(Filters.command, random_command))
    dp.add_handler(MessageHandler(Filters.all, random_message))
