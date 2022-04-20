from telegram import Update, BotCommandScopeChat
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from database.models import User
from utils.literals import Info
from config import ADMIN_PASSWORD
from utils.startup import DEFAULT_COMMANDS
from .commands import ADMIN_COMMANDS


def login(update: Update, context: CallbackContext):
    message = update.message
    args = context.args

    if args and args[0] == ADMIN_PASSWORD:
        admin: User = User.get(message.from_user.id)
        if admin.status != "admin":
            admin.status = "admin"
            admin.save()
        message.delete()
        context.bot.set_my_commands(
            commands=ADMIN_COMMANDS + DEFAULT_COMMANDS,
            scope=BotCommandScopeChat(chat_id=message.chat_id),
        )
        message.reply_text(
            f"{message.from_user.full_name}, вы вошли в систему как <b>{admin.status}</b>.\n"
            f"Ваши команды обновлены.\n\n"
            f"Про режим администратора: /help")
    else:
        message.reply_text("Неизвестная команда.\n\n" + Info.COMMANDS_HINT)


def logout(update: Update, context: CallbackContext):
    message = update.message
    user: User = User.get(message.from_user.id)

    if user.status == "admin":
        user.status = "user"
        user.save()
        context.bot.set_my_commands(
            commands=DEFAULT_COMMANDS,
            scope=BotCommandScopeChat(chat_id=message.chat_id),
        )
        message.reply_text(f"{message.from_user.full_name}, вы вошли в систему как <b>{user.status}</b>.\n"
                           f"Ваши команды обновлены.")
    else:
        message.reply_text("Неизвестная команда.\n\n" + Info.COMMANDS_HINT)


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("logout", logout))
