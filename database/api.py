from typing import Union

from telegram import Update
from telegram.ext import CallbackContext

from peewee import DoesNotExist

from .models import User


def get_user(user_id: int) -> Union[User, None]:
    try:
        return User.get(id=user_id)
    except DoesNotExist:
        return None


def check_user(handler):
    def wrapper(update: Update, context: CallbackContext):
        from_user = update.message.from_user

        if not get_user(from_user.id):
            username = from_user.username
            if not username:
                username = ""

            User.create(
                id=from_user.id,
                status="user",
                name=from_user.full_name,
                username=username,
            )

        return handler(update, context)

    return wrapper
