from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def product_keyboard(index: int, products_len: int) -> InlineKeyboardMarkup:
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
