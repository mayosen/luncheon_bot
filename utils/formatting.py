from datetime import datetime
from typing import List

from database.api import get_all_orders, get_completed_orders
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


def format_user(user: User, admin=False) -> str:
    text = (
        f"{'Пользователь' if user.status == 'user' else 'Администратор'} {user.name}\n",
        f"ID: {str(user)}\n\n",
        f"Дата регистрации: {format_date(user.joined, full=True)}\n" if admin else "",
        f"Телефон: <code>{user.phone}</code>\n",
        f"Адрес: <code>{user.address}</code>\n\n",
        f"Всего заказов: {len(get_all_orders(user))}" if admin else f"Заказов: {len(get_completed_orders(user))}",
    )

    return "".join(text)
