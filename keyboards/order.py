from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.literals import Symbols


def product_keyboard(next_category: str, index: int, products_len: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"Далее: {next_category}",
                callback_data=f"user:next_state",
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"user:cart:{index}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=Symbols.PREVIOUS,
                callback_data=f"user:index:{products_len - 1 if (index == 0) else index - 1}",
            ),
            InlineKeyboardButton(
                text=Symbols.NEXT,
                callback_data=f"user:index:{0 if (index == products_len - 1) else index + 1}",
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
