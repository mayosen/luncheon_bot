from typing import List

from telegram import BotCommand
from telegram import Bot
from telegram.error import Unauthorized

from database.api import get_admins, get_order_products
from database.models import Order
from keyboards.profile import order_keyboard
from utils.formatting import format_order, format_date

DEFAULT_COMMANDS = [
    BotCommand("order", "Сделать заказ"),
    BotCommand("cancel", "Отменить действие"),
    BotCommand("me", "Ваш профиль"),
]


def set_default_commands(bot: Bot):
    bot.set_my_commands(DEFAULT_COMMANDS)


def on_startup_notification(bot: Bot):
    admins = get_admins()
    for admin in admins:
        try:
            bot.send_message(chat_id=admin.id, text="<i>Бот запущен.</i>")
        except Unauthorized:
            continue


def clean_unprocessed_orders(bot: Bot):
    orders: List[Order] = Order.select().where(Order.status == "подтверждение")
    for order in orders:
        order.status = "отклонен"
        order.feedback = "Заказ не обработан администратором"
        order.save()

        products = get_order_products(order)
        text = (
                f"Пожалуйста, повторите заказ <code>#{order.id}</code>\n"
                f"Ни один администратор не обработал его.\n"
                f"Дата: {format_date(order.created, full=True)}\n\n"
                + format_order(order, products)
        )
        feedback_exists = order.feedback and order.status != "отклонен"

        try:
            bot.send_message(
                chat_id=order.user.id,
                text=text,
                reply_markup=order_keyboard(order.id, feedback_exists),
            )
        except Unauthorized:
            continue
