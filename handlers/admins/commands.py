import re
from statistics import mean
from typing import List
from collections import Counter

from telegram import Update, Message, BotCommand, InputMediaPhoto, ChatAction
from telegram.error import Unauthorized
from telegram.ext import Dispatcher, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler

import database.api as api
from database.models import Order, User
from filters import is_admin
from filters.cancel import cancel_filter
from handlers.admins.errors import ask_admins
from keyboards.profile import order_history_keyboard
import keyboards.admin as keyboards
from utils.formatting import format_order, format_date, format_user

MAILING = 0

ADMIN_COMMANDS = [
    BotCommand("admins", "Список активных администраторов"),
    BotCommand("users", "Список пользователей"),
    BotCommand("user", "Профиль пользователя"),
    BotCommand("delete", "Удалить пользователя"),
    BotCommand("getorder", "Карточка заказа"),
    BotCommand("rates", "Общий рейтинг заказов"),
    BotCommand("product", "Карточка продукта"),
    BotCommand("mailing", "Рассылка пользователям"),
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
             "/mailing - рассылка пользователям\n"
             "/logout - выход из режима администратора\n\n"
    )


def view_admins(update: Update, context: CallbackContext):
    admins = api.get_admins()
    admin_mentions = [f"{admin.name} {admin}" for admin in admins]
    text = []
    for number, admin in enumerate(admin_mentions):
        text.append(f"{number + 1} - {admin}")

    update.message.reply_text(f"Активных администраторов: {len(admin_mentions)}\n\n" + "\n".join(text))


def view_users(update: Update, context: CallbackContext):
    users = api.get_users()
    user_mentions = [f"{user.name} {user}" for user in users]
    text = []
    for number, admin in enumerate(user_mentions):
        text.append(f"{number + 1} - {admin}")

    update.message.reply_text(f"Пользователей: {len(user_mentions)}\n\n" + "\n".join(text))


def total_rates(update: Update, context: CallbackContext):
    total_orders: List[Order] = Order.select().where(Order.status == "выполнен")
    orders: List[Order] = Order.select().where(Order.rate != 0)
    rates = [order.rate for order in orders]
    rate_counter = Counter(rates)
    rate_items = sorted(rate_counter.items())
    text = []
    for rate, count in rate_items:
        text.append(f"<b>{rate}</b> - {count} заказов")

    update.message.reply_text(
        f"Выполненных заказов: {len(total_orders)}\n"
        f"Оцененных заказов: {len(orders)}\n\n"
        + "\n".join(text) +
        f"\n\nСредняя оценка: <b>{mean(rates): .2f}</b>"
    )


def view_user(update: Update, context: CallbackContext):
    message = update.message
    if not context.args:
        message.reply_text("Отправьте аргументом команды <code>id</code> или <code>username</code> пользователя.")
        return

    arg = context.args[0]
    user = api.get_user(arg)

    if not user:
        message.reply_text("Пользователь не найден.")
    else:
        text = format_user(user, admin=True)
        message.reply_text(text, reply_markup=keyboards.user_profile_keyboard(user.id) if user.orders else None)


def view_user_history(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
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


def delete_user(update: Update, context: CallbackContext):
    message = update.message

    if not context.args:
        message.reply_text("Отправьте аргументом команды <code>id</code> пользователя.")
        return

    arg = context.args[0]
    user = api.get_user(arg)

    if not user:
        message.reply_text("Пользователь не найден.")
    else:
        user.delete_instance(recursive=True)
        message.reply_text("Пользователь удален.")


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
    else:
        reply_with_order(message, order)


def view_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    order_id = int(re.match(r"admin:order:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    reply_with_order(query.message, order)


def reply_with_order(message: Message, order: Order):
    products = api.get_order_products(order)
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


def ask_mailing(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text(f"Активных пользователей: {len(api.get_users())}")
    asking = message.reply_text(
        text="Отправьте одно сообщение с фотографией или без.\n"
             "При необходимости отредактируйте его, затем нажмите кнопку "
             "<b>Начать рассылку</b>\n\n"
             "Для отмены введите /cancel",
        reply_markup=keyboards.mailing_keyboard,
    )
    context.user_data["mailing"] = {
        "asking": asking,
        "content": None,
    }

    return MAILING


def cancel_mailing(update: Update, context: CallbackContext):
    update.message.reply_text("Рассылка отменена.")
    asking: Message = context.user_data["mailing"]["asking"]
    context.bot.edit_message_reply_markup(
        chat_id=asking.chat_id,
        message_id=asking.message_id,
    )
    context.user_data.clear()

    return ConversationHandler.END


def get_mailing_content(update: Update, context: CallbackContext):
    message = update.edited_message if update.edited_message else update.message
    context.user_data["mailing"]["content"] = message


def do_mailing(update: Update, context: CallbackContext):
    query = update.callback_query
    content: Message = context.user_data["mailing"]["content"]

    if not content:
        query.answer()
        query.message.reply_text("Пожалуйста, введите текст или прикрепите фотографию.")
        return

    query.edit_message_reply_markup()
    query.message.reply_chat_action(ChatAction.TYPING)
    users = User.select()
    fails = []
    bot = context.bot

    if content.photo:
        photo = content.photo[-1].file_id
        caption = content.caption
        for user in users:
            try:
                bot.send_photo(
                    chat_id=user.id,
                    photo=photo,
                    caption=caption,
                )
            except Unauthorized:
                fails.append(user)
                continue
    else:
        text = content.text
        for user in users:
            try:
                bot.send_message(
                    chat_id=user.id,
                    text=text,
                )
            except Unauthorized:
                fails.append(user)
                continue

    context.user_data.clear()
    query.message.reply_text(f"Рассылка закончена.\nНеудач при отправке: {len(fails)}")

    for user in fails:
        ask_admins(user, bot)

    return ConversationHandler.END


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("help", get_help, filters=is_admin))
    dp.add_handler(CommandHandler("admins", view_admins, filters=is_admin))
    dp.add_handler(CommandHandler("users", view_users, filters=is_admin))
    dp.add_handler(CommandHandler("rates", total_rates, filters=is_admin))
    dp.add_handler(CommandHandler("delete", delete_user, filters=is_admin))

    dp.add_handler(CommandHandler("user", view_user, filters=is_admin))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:history:\d+$", callback=view_user_history))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:page:\d+:(\d+|pass)$", callback=switch_page))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:order:\d+$", callback=view_order))
    dp.add_handler(CallbackQueryHandler(pattern=r"^admin:feedback:existing:\d+$", callback=view_feedback))
    dp.add_handler(CommandHandler("getorder", view_order_command, filters=is_admin))
    dp.add_handler(CommandHandler("product", view_product, filters=is_admin))

    mailing_handler = ConversationHandler(
        entry_points=[
            CommandHandler("mailing", ask_mailing, filters=is_admin),
        ],
        states={
            MAILING: [
                MessageHandler(
                    filters=(
                        (Filters.text & ~Filters.command & ~cancel_filter)
                        | Filters.update.edited_message
                        | Filters.photo
                    ),
                    callback=get_mailing_content,
                ),
                CallbackQueryHandler(pattern=r"^admin:mailing:start$", callback=do_mailing),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_mailing),
            MessageHandler(cancel_filter, cancel_mailing),
        ],
    )

    dp.add_handler(mailing_handler)
