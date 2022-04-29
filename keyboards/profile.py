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


def order_history_keyboard(user_id: int, orders: List[Order], current_index: int, admin=False) -> InlineKeyboardMarkup:
    keyboard = []
    total_orders = len(orders)
    orders_per_page = 7
    right_delta = orders_per_page if (total_orders - current_index > orders_per_page) \
        else total_orders - current_index
    scope = "admin" if admin else "user"

    for index in range(current_index, current_index + right_delta):
        order = orders[index]
        date = format_date(order.created)
        text = f"[{index + 1}] Заказ #{order.id} от {date}"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"{scope}:order:{order.id}"
                )
            ]
        )

    left_border = (current_index == 0)
    right_border = (current_index + orders_per_page >= total_orders)

    if total_orders > orders_per_page:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=Symbols.BORDER if left_border else Symbols.PREVIOUS,
                    callback_data=f"{scope}:page:{user_id}:"
                                  + ("pass" if left_border else f"{current_index - orders_per_page}"),
                ),
                InlineKeyboardButton(
                    text=Symbols.BORDER if right_border else Symbols.NEXT,
                    callback_data=f"{scope}:page:{user_id}:"
                                  + ("pass" if right_border else f"{current_index + orders_per_page}"),
                ),
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def order_keyboard(order_id: int, feedback_exists: bool = None) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Повторить заказ",
                callback_data=f"user:reorder:{order_id}",
            ),
        ]
    ]

    if feedback_exists is not None:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Посмотреть отзыв" if feedback_exists else "Добавить отзыв",
                    callback_data=f"user:feedback:existing:{order_id}"
                    if feedback_exists else f"user:feedback:{order_id}",
                ),
            ]
        )

    return InlineKeyboardMarkup(keyboard)
