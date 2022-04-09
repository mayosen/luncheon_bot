from telegram import Update
from telegram.ext import Dispatcher, CallbackContext
from telegram.ext import MessageHandler

from filters import is_admin


def admin_echo(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=update.message.text,
    )


def register(dp: Dispatcher):
    dp.add_handler(MessageHandler(is_admin, admin_echo))
