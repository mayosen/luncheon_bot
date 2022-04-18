from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from database.models import User
from utils.literals import Info
from config import ADMIN_PASSWORD


def login(update: Update, context: CallbackContext):
    message = update.message
    args = context.args

    for arg in args:
        if arg == ADMIN_PASSWORD:
            admin: User = User.get(message.from_user.id)
            if admin.status != "admin":
                admin.status = "admin"
                admin.save()
            message.delete()
            message.reply_text(
                f"{message.from_user.full_name}, вы вошли в систему как <b>{admin.status}</b>.\n\n"
                f"Про режим администратора: /help")
            return
    else:
        message.reply_text("Неизвестная команда.\n\n" + Info.COMMANDS_HINT)


def logout(update: Update, context: CallbackContext):
    message = update.message
    user: User = User.get(message.from_user.id)

    if user.status == "admin":
        user.status = "user"
        user.save()
        message.reply_text(f"{message.from_user.full_name}, вы вошли в систему как <b>{user.status}</b>.")
    else:
        message.reply_text("Неизвестная команда.\n\n" + Info.COMMANDS_HINT)


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("logout", logout))
