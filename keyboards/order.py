from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def product_keyboard(index: int, products_len: int) -> InlineKeyboardMarkup:
    left_border = (index == 0)
    right_border = (index == products_len - 1)

    buttons = [
        [
            InlineKeyboardButton(
                text="Следующий этап",
                callback_data=f"user:next_state",
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"user:cart:{index}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="×" if left_border else "<",
                callback_data="user:index:" + ("pass" if left_border else f"{index - 1}"),
            ),
            InlineKeyboardButton(
                text="×" if right_border else ">",
                callback_data="user:index:" + ("pass" if right_border else f"{index + 1}"),
            ),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


phone_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Использовать прошлый номер",
                callback_data="user:last_phone",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ввести новый",
                callback_data="user:new_phone",
            ),
        ],
    ]
)


address_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Использовать прошлый адрес",
                callback_data="user:last_address",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ввести новый",
                callback_data="user:new_address",
            ),
        ],
    ]
)


def order_action_keyboard(empty_cart=False) -> InlineKeyboardMarkup:
    keyboard = []

    if not empty_cart:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Подтвердить заказ",
                    callback_data="user:confirm",
                ),
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="Собрать заказ заново",
                callback_data="user:reorder",
            ),
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="Отменить заказ",
                callback_data="user:cancel",
            ),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def rate_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=str(rate),
                callback_data=f"user:rate:{order_id}:{rate}"
            ) for rate in range(1, 6)
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


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
