from typing import Union, List

from telegram import Update
from telegram.ext import CallbackContext
from peewee import DoesNotExist

from .models import User, Order


def get_user(user_id: int) -> Union[User, None]:
    try:
        return User.get(id=user_id)
    except DoesNotExist:
        return None


def check_user(handler):
    def wrapper(update: Update, context: CallbackContext):
        from_user = update.message.from_user if update.message else update.callback_query.from_user

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


def get_admins() -> List[User]:
    admins: List[User] = User.select().where(User.status == "admin")
    return admins


def get_user_completed_orders(user: User) -> List[Order]:
    orders: List[Order] = user.orders.where(Order.status == "выполнен")
    return orders
