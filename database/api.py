from typing import Union, List

from telegram import Update
from telegram.ext import CallbackContext
from peewee import DoesNotExist

from models import User, Order, Product


def get_user(identifier: Union[int, str]) -> Union[User, None]:
    try:
        if isinstance(identifier, int) or identifier.isdigit():
            return User.get(id=int(identifier))
        else:
            return User.get(username=identifier.lower())
    except DoesNotExist:
        return None


def check_user(handler):
    def wrapper(update: Update, context: CallbackContext):
        from_user = update.message.from_user if update.message else update.callback_query.from_user

        if not get_user(from_user.id):
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


def get_order_products(order: Order) -> List[Product]:
    products: List[Product] = [item.product for item in order.items]
    return products


def get_product(product_id: int) -> Union[Product, None]:
    try:
        return Product.get(id=product_id)
    except DoesNotExist:
        return None
