from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database.models import Product


def product_keyboard(current: int, products: List[Product]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"cart:{products[current].id}"
            ),
        ],
        [],
    ]

    if current == 0:
        buttons[1] = [
            InlineKeyboardButton(
                text=">",
                callback_data=f"index:{current + 1}"
            ),
        ]
    elif current == len(products) - 1:
        buttons[1] = [
            InlineKeyboardButton(
                text="<",
                callback_data=f"index:{current - 1}"
            ),
        ]
    else:
        buttons[1] = [
            InlineKeyboardButton(
                text="<",
                callback_data=f"index:{current - 1}"
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=f"index:{current + 1}"
            ),
        ]

    return InlineKeyboardMarkup(buttons)
