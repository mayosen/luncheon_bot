from typing import Union, List

from telegram import Update
from telegram.ext import CallbackContext
from peewee import DoesNotExist

from .models import User, Order, Product


def get_user(user_id: int = 0, username: str = None) -> Union[User, None]:
    if not any((user_id, username)):
        return None
    try:
        return User.get(id=user_id) if user_id else User.get(username=username.lower())
    except DoesNotExist:
        return None


def check_user(handler):
    def wrapper(update: Update, context: CallbackContext):
        from_user = update.message.from_user if update.message else update.callback_query.from_user

        if not get_user(user_id=from_user.id):
            username = from_user.username.lower() if from_user.username else ""

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


def get_users() -> List[User]:
    admins: List[User] = User.select().where(User.status == "user")
    return admins


def get_completed_orders(user: User) -> List[Order]:
    orders: List[Order] = user.orders.where(Order.status == "выполнен")
    return orders


def get_all_orders(user: User) -> List[Order]:
    orders: List[Order] = user.orders
    return orders


def get_order(order_id: int) -> Union[Order, None]:
    try:
        return Order.get(id=order_id)
    except DoesNotExist:
        return None


def get_product(product_id: int) -> Union[Product, None]:
    try:
        return Product.get(id=product_id)
    except DoesNotExist:
        return None
