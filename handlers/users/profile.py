import re
from typing import List

from telegram import Update, MessageEntity, Message
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.api import check_user, get_completed_orders
from database.models import User, Order, Product
from filters.cancel import cancel_filter
import keyboards.profile as keyboards
from utils.formatting import format_order, format_date

PHONE = 0
ADDRESS = 0


@check_user
def user_profile(update: Update, context: CallbackContext):
    user = User.get(id=update.message.from_user.id)
    status = "Пользователь" if user.status == "user" else "Администратор"
    update.message.reply_text(
        text=f"{status} {str(user)}\n\n"
             f"Телефон: <code>{user.phone}</code>\n"
             f"Адрес: <code>{user.address}</code>\n\n"
             f"Заказов: {len(get_completed_orders(user))}",
        reply_markup=keyboards.profile_keyboard(user.id),
    )


def order_history(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user = User.get(id=query.from_user.id)
    orders = get_completed_orders(user)

    if len(orders) > 0:
        query.message.reply_text(
            text=f"{query.from_user.full_name}, ваши заказы",
            reply_markup=keyboards.order_history_keyboard(0, orders),
        )
    else:
        query.message.reply_text(f"{query.from_user.full_name}, у вас еще нет заказов.")


def switch_page(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = re.match(r"user:history:order:(\w+)", query.data).group(1)

    if data == "pass":
        query.answer()
        return
    else:
        new_index = int(data)

    orders = get_completed_orders(User.get(id=query.from_user.id))
    query.message.edit_reply_markup(keyboards.order_history_keyboard(new_index, orders))


def open_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    order_id = int(re.match(r"user:order:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    products: List[Product] = [item.product for item in order.items]

    text = (
        f"Заказ <code>#{order.id}</code>\n"
        f"Дата: {format_date(order.created, full=True)}\n\n"
        + format_order(order, products)
    )

    feedback_exists = order.feedback and order.status != "отклонен"
    query.message.reply_text(
        text=text,
        reply_markup=keyboards.order_keyboard(order_id, feedback_exists),
    )


def change_phone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("Введите ваш номер телефона или отправьте контакт.\n\n"
                             "Для отмены введите /cancel")

    return PHONE


def incorrect_phone(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Пожалуйста, введите корректный номер телефона.\n"
        "Он нужен, чтобы связаться с вами в случае возникновения затруднений."
    )


def update_phone(message: Message):
    phone = message.contact.phone_number if message.contact else message.text

    if len(phone) == 10:
        phone = "+7" + phone
    elif len(phone) == 11:
        phone = "+" + phone

    user = User.get(id=message.from_user.id)
    user.phone = phone
    user.save()

    return user


def get_phone(update: Update, context: CallbackContext):
    message = update.message
    update_phone(message)
    message.reply_text("Ваш номер телефона изменен.")

    return ConversationHandler.END


def change_address(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("Введите новый адрес или отправьте локацию.\n\n"
                             "Для отмены введите /cancel")

    return ADDRESS


def update_address(message: Message):
    if message.location:
        address = f"{message.location.latitude}, {message.location.longitude}"
    else:
        address = message.text

    user = User.get(id=message.from_user.id)
    user.address = address
    user.save()

    return user


def get_address(update: Update, context: CallbackContext):
    message = update.message
    update_address(message)
    message.reply_text("Ваш адрес изменен.")

    return ConversationHandler.END


def cancel_change(update: Update, context: CallbackContext):
    update.message.reply_text("Изменение данных отменено.")

    return ConversationHandler.END


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("me", user_profile))
    dp.add_handler(CallbackQueryHandler(pattern=r"^user:history:\d+$", callback=order_history))
    dp.add_handler(CallbackQueryHandler(pattern=r"^user:history:order:(\d+|pass)$", callback=switch_page))
    dp.add_handler(CallbackQueryHandler(pattern=r"^user:order:\d+$", callback=open_order))

    phone_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=r"^user:phone:\d+$", callback=change_phone),
        ],
        states={
            PHONE: [
                MessageHandler(Filters.entity(MessageEntity.PHONE_NUMBER) | Filters.contact, get_phone),
                MessageHandler(Filters.text & ~Filters.command & ~cancel_filter, incorrect_phone),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_change),
            MessageHandler(cancel_filter, cancel_change),
        ],
    )

    dp.add_handler(phone_handler)

    address_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=r"^user:address:\d+$", callback=change_address),
        ],
        states={
            ADDRESS: [
                MessageHandler((Filters.text & ~Filters.command & ~cancel_filter) | Filters.location, get_address),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_change),
            MessageHandler(cancel_filter, cancel_change),
        ],
    )

    dp.add_handler(address_handler)
