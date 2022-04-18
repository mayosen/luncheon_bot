from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database.models import Order
from utils.formatting import format_date
from utils.literals import Symbols


def profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="История заказов",
                callback_data=f"user:history:{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Изменить телефон",
                callback_data=f"user:phone:{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Изменить адрес",
                callback_data=f"user:address:{user_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def order_history_keyboard(current_index: int, orders: List[Order]) -> InlineKeyboardMarkup:
    keyboard = []
    orders_len = len(orders)
    orders_per_page = 5
    right_delta = orders_per_page if (orders_len - current_index > orders_per_page) else orders_len - current_index

    for index in range(current_index, current_index + right_delta):
        order = orders[index]
        date = format_date(order.created)
        text = f"[{index}] Заказ #{order.id} от {date}"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"user:order:{order.id}"
                )
            ]
        )

    left_border = (current_index == 0)
    right_border = (current_index + orders_per_page >= orders_len)

    keyboard.append(
        [
            InlineKeyboardButton(
                text=Symbols.BORDER if left_border else Symbols.PREVIOUS,
                callback_data="user:history:order:"
                              + ("pass" if left_border else f"{current_index - orders_per_page}"),
            ),
            InlineKeyboardButton(
                text=Symbols.BORDER if right_border else Symbols.NEXT,
                callback_data="user:history:order:"
                              + ("pass" if right_border else f"{current_index + orders_per_page}"),
            ),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def order_keyboard(order_id: int, feedback_exists: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Повторить заказ",
                callback_data=f"user:reorder:{order_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Посмотреть отзыв" if feedback_exists else "Добавить отзыв",
                callback_data=f"user:feedback:existing:{order_id}"
                if feedback_exists else f"user:feedback:{order_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
