from telegram import Update
from telegram.ext import Dispatcher, CallbackContext
from telegram.ext import Filters, MessageHandler


def random_command(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда.\n\nИспользуйте одну из следующих команд:\n"
                              "/order - сделать новый заказ\n"
                              "/me - просмотреть ваш профиль\n")


def random_message(update: Update, context: CallbackContext):
    update.message.reply_text("Я не понимаю вас.\n\nИспользуйте одну из следующих команд:\n"
                              "/order - сделать новый заказ\n"
                              "/me - просмотреть ваш профиль\n")


def register(dp: Dispatcher):
    dp.add_handler(MessageHandler(Filters.command, random_command))
    dp.add_handler(MessageHandler(Filters.all, random_message))
