from datetime import datetime
from typing import List

from database.models import Product, User


def format_items(products: List[Product], admin=False):
    positions = [f"[id: {product.id}] {product}" for product in products] if admin \
            else [f"- {product}" for product in products]

    formatted = "\n".join(positions)
    cost = sum([product.price for product in products])

    return f"Позиции меню:\n{formatted}\n\nСумма: <b>{cost}</b> р."


def format_order(user: User, products: List[Product], admin=False):
    positions = format_items(products, admin)
    text = (
        f"Телефон: <code>{user.phone}</code>\n"
        f"Адрес: <code>{user.address}</code>\n\n"
        f"{positions}"
    )

    return text


def format_date(date: datetime, full=False):
    return date.strftime("%d.%m.%Y %H:%M") if full else date.strftime("%d.%m")
