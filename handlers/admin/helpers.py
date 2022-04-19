from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Dispatcher, CallbackContext, Filters, CommandHandler, ConversationHandler
from telegram.ext import MessageHandler

from filters import is_admin
from filters.cancel import cancel_filter

COLLECT = 0


def get_help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Команды администратора\n\n"
             "/login \"password\" - вход с паролем\n"
             "/logout - выход",
        # TODO: Дополнить
    )


def to_photo(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Отправьте <b>file_id</b> как аргумент команды.")
        return

    file_id = context.args[0]
    try:
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=file_id,
        )
    except BadRequest as error:
        update.message.reply_text(f"Ошибка: {error}")


def collect_photos(update: Update, context: CallbackContext):
    update.message.reply_text("Присылайте фотографии. А когда закончите, отправьте /stop, "
                              "чтобы получить их file_id.")
    context.user_data["photo"] = []

    return COLLECT


def to_file_id(update: Update, context: CallbackContext):
    photo = context.user_data["photo"]
    photo.append(update.message.photo[-1].file_id)


def send_file_ids(update: Update, context: CallbackContext):
    photo_list = context.user_data["photo"]
    context.user_data.clear()

    if photo_list:
        prepared = [f"{index + 1}: <code>{photo}</code>" for index, photo in enumerate(photo_list)]
        text = "\n\n".join(prepared)
        update.message.reply_text(text)
    else:
        update.message.reply_text("Вы не отправили фотографии.")

    return ConversationHandler.END


def cancel_collecting(update: Update, context: CallbackContext):
    update.message.reply_text("Отменено.")
    context.user_data.clear()

    return ConversationHandler.END


def register(dp: Dispatcher):
    dp.add_handler(CommandHandler("help", get_help))
    dp.add_handler(CommandHandler("file", to_photo, filters=is_admin))

    photo_handler = ConversationHandler(
        entry_points=[
            CommandHandler("photo", collect_photos, filters=is_admin),
        ],
        states={
            COLLECT: [
                MessageHandler(Filters.photo, to_file_id),
                CommandHandler("stop", send_file_ids),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_collecting),
            MessageHandler(cancel_filter, cancel_collecting),
        ],
    )

    dp.add_handler(photo_handler)
