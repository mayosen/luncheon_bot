from datetime import datetime
from typing import List

from database.models import Product, User


def format_items(products: List[Product]):
    positions = "".join([f"- {product}\n" for product in products])
    cost = sum([product.price for product in products])

    # TODO: Вынести сумму в отдельный заказ?

    return f"Позиции меню:\n{positions}\nСумма: <b>{cost}</b> р."


def format_order(user: User, products: List[Product]):
    positions = format_items(products)
    text = (
        f"Телефон: <code>{user.phone}</code>\n"
        f"Адрес: <code>{user.address}</code>\n\n"
        f"{positions}"
    )

    return text


def format_date(date: datetime, full=False):
    return date.strftime("%d.%m.%Y %H:%M") if full else date.strftime("%d.%m")
