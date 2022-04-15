from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def product_keyboard(index: int, products_len: int) -> InlineKeyboardMarkup:
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
                text="×" if index == 0 else "<",
                callback_data="user:index:" + ("pass" if index == 0 else f"{index - 1}"),
            ),
            InlineKeyboardButton(
                text="×" if index == products_len - 1 else ">",
                callback_data="user:index:" + ("pass" if index == products_len - 1 else f"{index + 1}"),
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
            ],
        )

    keyboard.append([
            InlineKeyboardButton(
                text="Собрать заказ заново",
                callback_data="user:reorder",
            ),
    ])

    keyboard.append([
        InlineKeyboardButton(
            text="Отменить заказ",
            callback_data="user:cancel",
        ),
    ])

    return InlineKeyboardMarkup(keyboard)


def rate_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="1",
                callback_data=f"user:rate:1:{order_id}",
            ),
            InlineKeyboardButton(
                text="2",
                callback_data=f"user:rate:2:{order_id}",
            ),
            InlineKeyboardButton(
                text="3",
                callback_data=f"user:rate:3:{order_id}",
            ),
            InlineKeyboardButton(
                text="4",
                callback_data=f"user:rate:4:{order_id}",
            ),
            InlineKeyboardButton(
                text="5",
                callback_data=f"user:rate:5:{order_id}",
            ),
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
