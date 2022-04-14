from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def product_keyboard(index: int, products_len: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Следующий этап",
                callback_data=f"next_state",
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"cart:{index}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="×" if index == 0 else "<",
                callback_data="index:" + ("pass" if index == 0 else f"{index - 1}"),
            ),
            InlineKeyboardButton(
                text="×" if index == products_len - 1 else ">",
                callback_data="index:" + ("pass" if index == products_len - 1 else f"{index + 1}"),
            ),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


phone_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Использовать прошлый номер",
                callback_data="last_phone",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ввести новый",
                callback_data="new_phone",
            ),
        ],
    ]
)


address_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Использовать прошлый адрес",
                callback_data="last_address",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ввести новый",
                callback_data="new_address",
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
