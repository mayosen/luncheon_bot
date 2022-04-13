from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_product_keyboard(index: int, products_len: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"cart:{index}"
            ),
        ],
        [],
    ]

    if index == 0:
        buttons[1] = [
            InlineKeyboardButton(
                text=">>",
                callback_data=f"index:{index + 1}"
            ),
        ]
    elif index == products_len - 1:
        buttons[1] = [
            InlineKeyboardButton(
                text="<<",
                callback_data=f"index:{index - 1}"
            ),
        ]
    else:
        buttons[1] = [
            InlineKeyboardButton(
                text="<<",
                callback_data=f"index:{index - 1}"
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=f"index:{index + 1}"
            ),
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
        ]
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
        ]
    ]
)

order_action_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Подтвердить заказ",
                callback_data="user:confirm",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Собрать заказ заново",
                callback_data="user:reorder",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отменить заказ",
                callback_data="user:cancel",
            ),
        ],
    ]
)
