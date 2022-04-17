from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def approve_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Принять заказ",
                callback_data=f"admin:approve:{order_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отклонить заказ",
                callback_data=f"admin:reject:{order_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Готовится",
                callback_data=f"admin:status:готовится:{order_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Передан в доставку",
                callback_data=f"admin:status:доставка:{order_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Выполнен",
                callback_data=f"admin:status:выполнен:{order_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
