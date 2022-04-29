import logging
import re
import traceback
from typing import Union, List
from json import dumps

from telegram import Update, Bot
from telegram.ext import Dispatcher, CallbackContext, CallbackQueryHandler
from telegram.error import Unauthorized

from database.api import get_admins, get_user
from database.models import User, Log
from keyboards.admin import block_user, user_profile_keyboard
from utils.formatting import format_user


def error_dispatcher(update: Union[object, Update], context: CallbackContext):
    error = context.error
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    exception = Log.create(
        exception=type(error).__name__,
        message=str(error),
        args=str(error.args),
        traceback=traceback.format_exc(),
        user_data=dumps(context.user_data, ensure_ascii=False, default=lambda item: str(item)),
    )

    if isinstance(update, Update):
        exception.update_message = dumps(update.effective_message.to_dict(), ensure_ascii=False)
        exception.update_chat = dumps(update.effective_chat.to_dict(), ensure_ascii=False)
        exception.update_user = dumps(update.effective_user.to_dict(), ensure_ascii=False)
        exception.save()

        if isinstance(error, Unauthorized):
            unauthorized(update, context)
            return

    bot = context.bot
    admins = get_admins()
    trace = "<code>" + exception.traceback + "</code>"
    text = (
        f"Исключение при работе бота.\n\n"
        f"<b>{exception.exception}</b>: {exception.message}\n"
        f"<b>args</b>: {exception.args}\n"
        f"<b>user_data</b>: <code>{exception.user_data.replace('<', '').replace('>', '')}</code>"
    )
    update_info = "" if not exception.update_message \
        else (f"<b>Message</b>: <code>{exception.update_message.replace('<', '').replace('>', '')}</code>\n\n"
              f"<b>Chat</b>: <code>{exception.update_chat}</code>\n\n"
              f"<b>User</b>: <code>{exception.update_user}</code>")

    for admin in admins:
        bot.send_message(
            chat_id=admin.id,
            text=text,
        )
        if update_info:
            bot.send_message(
                chat_id=admin.id,
                text=update_info,
            )
        bot.send_message(
            chat_id=admin.id,
            text=trace,
        )


def unauthorized(update: Update, context: CallbackContext):
    if update:
        user_id = update.effective_user.id
        user = get_user(user_id)
        admins = get_admins()
        ask_admins(user, admins, context.bot)
        context.user_data.clear()
        context.bot_data.clear()


def ask_admins(user: User, admins: List[User], bot: Bot):
    for admin in admins:
        bot.send_message(
            chat_id=admin.id,
            text=f"Пользователь {user} заблокировал бота.\n",
            reply_markup=block_user(user.id),
        )
        bot.send_message(
            chat_id=admin.id,
            text=format_user(user),
            reply_markup=user_profile_keyboard(user.id)
        )


def on_user_action(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    data = re.match(r"admin:user:(delete|pass):(\d+)", query.data)
    action = data.group(1)

    if action == "pass":
        return

    user_id = int(data.group(2))
    user = get_user(user_id)

    if user:
        user.delete_instance(recursive=True)
    else:
        query.message.reply_text("Пользователь уже удален другим администратором.")


def register(dp: Dispatcher):
    dp.add_error_handler(error_dispatcher)
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:user:(delete|pass):\d+$", callback=on_user_action))
