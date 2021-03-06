from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def feedback_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Оставить отзыв",
                callback_data=f"user:feedback:{order_id}",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


create_feedback_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Отправить отзыв",
                callback_data="user:feedback:create",
            )
        ]
    ]
)


def change_feedback_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить отзыв",
                callback_data=f"user:feedback:{order_id}:re",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
