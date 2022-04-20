import re
from typing import List
from collections import Counter

from telegram import Update, Message, BotCommand, InputMediaPhoto
from telegram.ext import Dispatcher, CallbackContext
from telegram.ext import CommandHandler, CallbackQueryHandler

import database.api as api
from database.models import Order, User, Product
from filters import is_admin
import keyboards.admin as keyboards
from keyboards.profile import order_history_keyboard
from utils.formatting import format_order, format_date

ADMIN_COMMANDS = [
    BotCommand("admins", "Список активных администраторов"),
    BotCommand("user", "Профиль пользователя"),
    BotCommand("getorder", "Карточка заказа"),
    BotCommand("rates", "Общий рейтинг заказов"),
    BotCommand("product", "Карточка продукта"),
    BotCommand("logout", "Выход из режима администратора"),
]


def get_help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Команды администратора\n\n"
             "/login <code>password</code> - вход как администратор\n"
             "/admins - список активных администраторов\n"
             "/user <code>id|username</code> - профиль пользователя\n"
             "/getorder <code>id</code> - карточка заказа\n"
             "/rates - общий рейтинг заказов\n"
             "/product <code>id</code> - карточка продукта\n"
             "/logout - выход из режима администратора\n\n"
    )


def view_admins(update: Update, context: CallbackContext):
    admins = api.get_admins()
    admin_mentions = [str(admin) for admin in admins]
    text = []
    for number, admin in enumerate(admin_mentions):
        text.append(f"{number + 1} - {admin}")

    update.message.reply_text(f"Активных администраторов: {len(admin_mentions)}\n\n" + "\n".join(text))


def total_rates(update: Update, context: CallbackContext):
    total_orders: List[Order] = Order.select().where(Order.status == "выполнен")
    orders: List[Order] = Order.select().where(Order.rate != 0)
    rate_counter = Counter([order.rate for order in orders])
    rate_items = sorted(rate_counter.items())
    text = []
    for rate, count in rate_items:
        text.append(f"\"<b>{rate}</b>\" - {count} заказов")

    update.message.reply_text(
        text=f"Выполненных заказов: {len(total_orders)}\n"
             f"Оцененных заказов: {len(orders)}\n\n"
             + "\n".join(text)
    )


def view_user(update: Update, context: CallbackContext):
    message = update.message
    if not context.args:
        message.reply_text("Отправьте аргументом команды <code>id</code> или <code>username</code> пользователя.")
        return

    identifier = context.args[0]
    user = api.get_user(user_id=int(identifier)) if identifier.isdigit() else api.get_user(username=identifier)
    if not user:
        message.reply_text("Пользователь не найден.")
        return

    status = "Пользователь" if user.status == "user" else "Администратор"
    update.message.reply_text(
        text=f"{status} {str(user)}\n\n"
             f"Телефон: <code>{user.phone}</code>\n"
             f"Адрес: <code>{user.address}</code>\n\n"
             f"Всего заказов: {len(api.get_all_orders(user))}",
        reply_markup=keyboards.user_profile_keyboard(user.id) if user.orders else None,
    )


def view_user_history(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = int(re.match(r"admin:history:(\d+)", query.data).group(1))
    user = User.get(id=user_id)
    orders = api.get_all_orders(user)
    query.message.reply_text(
        text="История заказов пользователя",
        reply_markup=order_history_keyboard(user_id, orders, 0, admin=True),
    )


def switch_page(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = re.match(r"admin:page:(\d+):(\w+)", query.data)
    user_id = int(data.group(1))
    new_index = data.group(2)

    if new_index == "pass":
        query.answer()
        return

    orders = api.get_all_orders(User.get(id=user_id))
    query.message.edit_reply_markup(order_history_keyboard(user_id, orders, int(new_index), admin=True))


def view_order_command(update: Update, context: CallbackContext):
    message = update.message
    if not context.args:
        message.reply_text("Отправьте аргументом команды <code>id</code> заказа.")
        return

    order_id = context.args[0]
    if not order_id.isdigit():
        message.reply_text("<code>id</code> заказа должно быть числом.")
        return

    order = api.get_order(int(order_id))
    if not order:
        message.reply_text("Заказ не найден.")
        return

    reply_with_order(message, order)


def view_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    order_id = int(re.match(r"admin:order:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)

    reply_with_order(query.message, order)


def reply_with_order(message: Message, order: Order):
    products: List[Product] = [item.product for item in order.items]
    text = (
            f"Заказ <code>#{order.id}</code>\n"
            f"Пользователь: {order.user}\n"
            f"Дата: {format_date(order.created, full=True)}\n"
            + ("" if order.rate == 0 else f"Оценка: {order.rate}\n") + "\n"
            + format_order(order, products, admin=True)
    )

    reply_markup = None
    if order.status == "отклонен":
        text += "\n\nЗаказ отклонен.\nПричина: " + (order.feedback if order.feedback else "не указано")
    elif order.feedback:
        reply_markup = keyboards.view_order_feedback(order.id)

    message.reply_text(text=text, reply_markup=reply_markup)


def view_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()

    order_id = int(re.match(r"admin:feedback:existing:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    text = order.feedback
    query.message.reply_text(f"Отзыв на заказ <code>#{order_id}</code>\n"
                             f"Пользователь: {order.user}\n\n" + text)

    if order.attachments:
        attachments: List = order.attachments.split(", ")
        media = [InputMediaPhoto(photo) for photo in attachments]
        query.message.reply_media_group(media=media)


def view_product(update: Update, context: CallbackContext):
    message = update.message
    if not context.args:
        message.reply_text("Отправьте аргументом команды <code>id</code> продукта.")
        return

    product_id = context.args[0]
    if not product_id.isdigit():
        message.reply_text("<code>id</code> продукта должно быть числом.")
        return

    product = api.get_product(int(product_id))
    if not product:
        message.reply_text("Продукт не найден.")
        return

    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price} р.",
    )


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("help", get_help, filters=is_admin))
    dp.add_handler(CommandHandler("admins", view_admins, filters=is_admin))
    dp.add_handler(CommandHandler("rates", total_rates, filters=is_admin))

    dp.add_handler(CommandHandler("user", view_user, filters=is_admin))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:history:\d+$", callback=view_user_history))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:page:\d+:(\d+|pass)$", callback=switch_page))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:order:\d+$", callback=view_order))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:feedback:existing:\d+$", callback=view_feedback))
    dp.add_handler(CommandHandler("getorder", view_order_command, filters=is_admin))

    dp.add_handler(CommandHandler("product", view_product, filters=is_admin))
