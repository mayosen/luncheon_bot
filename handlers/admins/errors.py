import re

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram.error import TelegramError

from database.api import get_admins, get_user
from keyboards.admin import block_user, user_profile_keyboard
from utils.formatting import format_user


def unauthorized(update: object, context: CallbackContext):
    error = context.error

    if not issubclass(error.__class__, TelegramError):
        # TODO: Обработка Python исключений
        return

    if "mailing" not in context.bot_data:
        # TODO: Обработка других Телеграм исключений
        return

    bot = context.bot
    user_id = context.bot_data["mailing"]["to_user"]
    user = get_user(user_id=user_id)
    admins = get_admins()

    for admin in admins:
        bot.send_message(
            chat_id=admin.id,
            text=f"Пользователь {user} заблокировал бота.\n"
                 f"<b>user_data</b>: {context.user_data}\n"
                 f"<b>bot_data</b>: {context.bot_data}",
            reply_markup=block_user(user.id),
        )
        bot.send_message(
            chat_id=admin.id,
            text=format_user(user),
            reply_markup=user_profile_keyboard(user.id)
        )

    context.user_data.clear()
    context.bot_data.clear()


def on_user_action(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    data = re.match(r"admin:user:(delete|pass):(\d+)", query.data)
    action = data.group(1)

    if action == "pass":
        return

    user_id = int(data.group(2))
    user = get_user(user_id=user_id)

    if user:
        user.delete_instance(recursive=True)
    else:
        query.message.reply_text("Пользователь уже удален другим администратором.")


def register(dp: Dispatcher):
    dp.add_error_handler(unauthorized)
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:user:(delete|pass):\d+$", callback=on_user_action))

