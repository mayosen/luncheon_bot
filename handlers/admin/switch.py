from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, Filters, CommandHandler
from telegram.ext import MessageHandler

from filters import is_admin
from database.models import User


def switch_status(update: Update, context: CallbackContext):
    admin: User = User.get(update.message.from_user.id)
    admin.status = "user" if admin.status == "admin" else "admin"
    admin.save()
    update.message.reply_text(f"Вы изменили статус на <b>{admin.status}</b>.")


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("switch", switch_status, filters=is_admin))
