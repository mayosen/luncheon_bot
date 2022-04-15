import re

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.models import Order, User
import keyboards.admin as keyboards
from keyboards.order import rate_order_keyboard


REJECT = 0


def approve_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    order_id = int(re.match(r"admin:approve:(\d+)", query.data).group(1))
    order: Order = Order.get(id=order_id)

    if order.status != "подтверждение":
        query.message.reply_text(f"Заказ <code>#{order_id}</code> обработан другим администратором.")
        return

    order.status = "принят"
    order.save()

    user: User = order.user
    admin: User = User.get(id=query.from_user.id)

    context.bot.send_message(
        chat_id=user.id,
        text=f"{user.name}, ваш заказ с номером <code>#{order_id}</code> принят.",
    )

    query.message.reply_text(
        text=f"{admin.name}, вы взяли заказ <code>#{order_id}</code>",
        reply_markup=keyboards.status_keyboard(order_id),
    )


def reject_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    order_id = int(re.match(r"admin:reject:(\d+)", query.data).group(1))
    order: Order = Order.get(id=order_id)

    if order.status != "подтверждение":
        query.message.reply_text(f"Заказ <code>#{order_id}</code> обработан другим администратором.")
        return

    context.user_data["to_reject"] = order
    query.message.reply_text(f"{query.from_user.full_name}, введите причину отказа.")

    return REJECT


def reject_reason(update: Update, context: CallbackContext):
    order: Order = context.user_data["to_reject"]
    del context.user_data["to_reject"]
    reason = update.message.text
    order.status = "отклонен"
    order.feedback = reason
    order.save()
    update.message.reply_text("Заказ отменен.")

    user: User = order.user
    context.bot.send_message(
        chat_id=user.id,
        text=f"{user.name}, ваш заказ <code>#{order.id}</code> отклонен.\n\n"
             f"Причина: {reason}",
    )

    return ConversationHandler.END


def cancel_reject(update: Update, context: CallbackContext):
    order: Order = context.user_data["to_reject"]
    del context.user_data["to_reject"]
    order.status = "подтверждение"
    order.save()
    update.message.reply_text(f"Заказ <code>#{order.id}</code> будет передан другому администратору.")

    return ConversationHandler.END


def set_order_status(update: Update, context: CallbackContext):
    query = update.callback_query
    data = re.match(r"admin:status:(\w+):(\d+)", query.data)
    status = data.group(1)
    order_id = int(data.group(2))
    order: Order = Order.get(id=order_id)

    if status == order.status:
        query.answer(f"Текущий статус: {status}")
        return

    query.answer(f"Вы поменяли статус: {status}")
    order.status = status
    order.save()
    query.message.edit_text(
        text=f"Заказ <code>#{order_id}</code>\n\n"
             f"Статус: {status}",
        reply_markup=None if status == "выполнен" else keyboards.status_keyboard(order_id),
    )

    if status == "готовится":
        user_info = "готовится"
    elif status == "доставка":
        user_info = "передан в доставку"
    elif status == "выполнен":
        user_info = "завершен"
    else:
        user_info = ""

    context.bot.send_message(
        chat_id=order.user.id,
        text=f"Ваш заказ <code>#{order_id}</code> {user_info}."
    )

    if status == "выполнен":
        context.bot.send_message(
            chat_id=order.user.id,
            text=f"{order.user.name}, пожалуйста, оцените заказ.",
            reply_markup=rate_order_keyboard(order_id),
        )


def register(dp: Dispatcher):
    dp.add_handler(CallbackQueryHandler(pattern=r"admin:approve:\d+", callback=approve_order))
    dp.add_handler(CallbackQueryHandler(pattern=r"admin:status:\w+", callback=set_order_status))
    rejection_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=r"admin:reject:\d+", callback=reject_order),
        ],
        states={
            REJECT: [
                MessageHandler(Filters.text, reject_reason),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_reject),
            MessageHandler(Filters.regex(re.compile(r".*(отмена|стоп).*", re.IGNORECASE)), cancel_reject),
        ],
    )
    dp.add_handler(rejection_handler)
