from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def feedback_order_keyboard(order_id: int, change=False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить отзыв" if change else "Оставить отзыв",
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
