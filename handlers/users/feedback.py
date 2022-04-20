import re
from typing import List, Dict

from telegram import Update, InputMediaPhoto, Message, ChatAction
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.api import get_admins
from database.models import Order
from filters.cancel import cancel_filter
from keyboards.feedback import create_feedback_keyboard, change_feedback_keyboard

FEEDBACK = 0


def feedback_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    user_data = context.user_data

    if not query.data.endswith("re"):
        query.message.reply_text(
            text="Ваш отзыв очень важен для нас.\n\n"
                 "О чем можно написать:\n"
                 "- разнообразие меню\n"
                 "- качество блюд\n"
                 "- скорость доставки\n\n"
                 "Кроме того, вы можете прислать фотографию вашего заказа."
        )

    sent: Message = query.message.reply_text(
        text="Отправьте необходимые сообщения и вложения, а затем "
             "нажмите кнопку <b>Отправить отзыв</b>\n\n"
             "Для отмены введите /cancel",
        reply_markup=create_feedback_keyboard,
    )
    user_data["feedback_message"] = sent

    order_id = int(re.match(r"user:feedback:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    user_data["feedback"] = {
        "order": order,
        "text": [],
        "attachments": [],
    }

    return FEEDBACK


def get_feedback(update: Update, context: CallbackContext):
    feedback: Dict = context.user_data["feedback"]
    message = update.message

    if message.photo:
        message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        feedback["attachments"].append(message.photo[-1].file_id)
        if message.caption:
            feedback["text"].append("photo: " + message.caption)

    elif message.text:
        message.reply_chat_action(ChatAction.TYPING)
        feedback["text"].append(message.text)


def create_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    feedback: Dict = context.user_data["feedback"]

    if not (feedback["text"] or feedback["attachments"]):
        query.answer()
        query.message.reply_text("Пожалуйста, введите текст или прикрепите фотографию.")
        return FEEDBACK

    query.edit_message_reply_markup()
    query.message.reply_text("Спасибо за подробный отзыв, мы учтем ваши пожелания!")
    order: Order = feedback["order"]
    order.feedback = ".\n".join(feedback["text"])
    order.attachments = ", ".join(feedback["attachments"])
    order.save()

    admins = get_admins()
    media = [InputMediaPhoto(photo) for photo in feedback["attachments"]]
    context.user_data.clear()

    for admin in admins:
        context.bot.send_message(
            chat_id=admin.id,
            text=f"Новый отзыв для заказа <code>#{order.id}</code>\n"
                 f"Пользователь: {order.user}\n\n"
                 + order.feedback
        )
        if media:
            context.bot.send_media_group(
                chat_id=admin.id,
                media=media,
            )

    return ConversationHandler.END


def cancel_feedback(update: Update, context: CallbackContext):
    update.message.reply_text("Отзыв отменен.")
    sent: Message = context.user_data["feedback_message"]
    context.bot.edit_message_reply_markup(
        chat_id=sent.chat_id,
        message_id=sent.message_id,
    )
    context.user_data.clear()

    return ConversationHandler.END


def existing_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    order_id = int(re.match(r"user:feedback:existing:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    text = order.feedback
    query.message.reply_text(
        text="Ваш отзыв\n\n" + text,
        reply_markup=change_feedback_keyboard(order_id),
    )

    if order.attachments:
        attachments: List = order.attachments.split(", ")
        media = [InputMediaPhoto(photo) for photo in attachments]
        query.message.reply_media_group(media=media)


def register(dp: Dispatcher):
    feedback_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=r"^user:feedback:\d+(:re)?$", callback=feedback_order),
        ],
        states={
            FEEDBACK: [
                MessageHandler((Filters.text & ~Filters.command & ~cancel_filter) | Filters.photo, get_feedback),
                CallbackQueryHandler(pattern=r"^user:feedback:create$", callback=create_feedback),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_feedback),
            MessageHandler(cancel_filter, cancel_feedback),
        ],
    )

    dp.add_handler(feedback_handler)
    dp.add_handler(CallbackQueryHandler(pattern=r"^user:feedback:existing:\d+$", callback=existing_feedback))
