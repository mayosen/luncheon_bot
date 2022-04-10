from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters


MAIN_DISH, SNACK, DRINK = range(3)


def make_order(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text("Начата сборка заказа.\nВыберите основное блюдо.")
    context.user_data["cart"] = []
    return MAIN_DISH


def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_text("Заказ отменен. Ждем вас еще!")
    return ConversationHandler.END


def get_main_dish(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    message.reply_text("Отлично!\nТеперь выберите закуску.")
    return SNACK


def get_snack(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    message.reply_text("Отлично!\nТеперь выберите напиток.")
    return DRINK


def get_drink(update: Update, context: CallbackContext):
    message = update.message
    context.user_data["cart"].append(message.text)
    # TODO: Кладем в базу
    message.reply_text("Спасибо!\nВаш заказ отправлен в обработку.")
    context.user_data.clear()
    return ConversationHandler.END


def register(dp: Dispatcher):
    order = ConversationHandler(
        entry_points=[CommandHandler("order", make_order)],
        states={
            MAIN_DISH: [
                MessageHandler(Filters.text & ~Filters.command, get_main_dish),
            ],
            SNACK: [
                MessageHandler(Filters.text & ~Filters.command, get_snack),
            ],
            DRINK: [
                MessageHandler(Filters.text & ~Filters.command, get_drink),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(order)
    # TODO: По окончании заказа чистить `user_data`
