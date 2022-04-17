from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from database.models import User

from config import ADMIN_PASSWORD
from utils.literals import COMMANDS_HINT


def login(update: Update, context: CallbackContext):
    message = update.message
    args = context.args

    for arg in args:
        if arg == ADMIN_PASSWORD:
            admin: User = User.get(message.from_user.id)
            if admin.status != "admin":
                admin.status = "admin"
                admin.save()
                message.reply_text(f"{message.from_user.full_name}, вы вошли в систему как <b>{admin.status}</b>.")
            else:
                message.reply_text(f"{message.from_user.full_name}, вы уже <b>{admin.status}</b>.")

            # TODO: admin /help

            return

    message.reply_text("Неизвестная команда.\n\n" + COMMANDS_HINT)


def logout(update: Update, context: CallbackContext):
    message = update.message
    user: User = User.get(message.from_user.id)

    if user.status == "admin":
        user.status = "user"
        user.save()
        message.reply_text(f"{message.from_user.full_name}, вы вошли в систему как <b>{user.status}</b>.")
        return
    else:
        message.reply_text("Неизвестная команда.\n\n" + COMMANDS_HINT)


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("logout", logout))