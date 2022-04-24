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


def user_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="История заказов",
                callback_data=f"admin:history:{user_id}",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def view_order_feedback(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Посмотреть отзыв",
                callback_data=f"admin:feedback:existing:{order_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def block_user(user_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Удалить пользователя",
                callback_data=f"admin:user:delete:{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Оставить в базе",
                callback_data=f"admin:user:pass:{user_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


mailing_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Начать рассылку",
                callback_data="admin:mailing:start",
            )
        ]
    ]
)
