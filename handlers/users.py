from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.ext import MessageHandler

from database.api import check_user
from database.models import User


@check_user
def get_me(update: Update, context: CallbackContext):
    user = User.get(id=update.message.from_user.id)
    update.message.reply_text(
        text=str(user),
    )


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("me", get_me))
