import re
from typing import List, Union
from datetime import datetime

from telegram import Update, Message, MessageEntity, CallbackQuery, InputMediaPhoto, ChatAction
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

import keyboards.order as keyboards
from filters.cancel import cancel_filter
from keyboards.admin import approve_keyboard
from database.api import check_user
from database.models import User, Product, Order, OrderItem

MAIN_DISH, SNACK, DRINK, PHONE, ADDRESS, CONFIRM = range(6)
FEEDBACK = 0


@check_user
def new_order(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data["cart"] = []

    if update.callback_query:
        message = update.callback_query.message
        to_process = update.callback_query
    else:
        message = update.message
        to_process = update.message

    message.reply_text(
        "Сборка заказа:\n"
        "- основное блюдо\n"
        "- закуска\n"
        "- напиток\n\n"
        "/cancel - отменить заказ"
    )
    process_state(to_process, "main_dish", "основное блюдо", context.user_data)

    return MAIN_DISH


def cancel_order(update: Update, context: CallbackContext):
    context.user_data.clear()
    message = update.callback_query.message if update.callback_query else update.message
    message.reply_text("Заказ отменен. Ждем вас еще!")

    return ConversationHandler.END


def switch_product(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = re.match(r"user:index:(\w+)", query.data).group(1)
    if data == "pass":
        return
    else:
        new_index = int(data)

    user_data = context.user_data
    products = user_data["cache"]
    product = products[new_index]

    query.message.edit_media(
        media=InputMediaPhoto(
            media=product.photo,
            caption=f"{product.title}\nЦена: {product.price} р.",
        ),
        reply_markup=keyboards.product_keyboard(new_index, len(products)),
    )


def add_to_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    index = int(re.match(r"user:cart:(\w+)", data).group(1))
    user_data = context.user_data
    product: Product = user_data["cache"][index]
    user_data["cart"].append(product)
    query.answer(f"Добавлено в корзину:\n{product}")


def process_state(update: Union[Message, CallbackQuery], category: str, alias: str, user_data: dict):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update

    products: List[Product] = Product.select().where(Product.category == category)
    user_data["cache"] = products
    index = 0
    product = products[index]

    message.reply_text(f"Выберите {alias}.")
    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price} р.",
        reply_markup=keyboards.product_keyboard(index, len(products)),
    )


def ask_snack(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    process_state(query, "snack", "закуску", context.user_data)

    return SNACK


def ask_drink(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    process_state(query, "drink", "напиток", context.user_data)

    return DRINK


def complete_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data

    if query.data != "user:next_state":
        index = int(re.match(r"user:cart:(\w+)", query.data).group(1))
        product = user_data["cache"][index]
        user_data["cart"].append(product[index])

    del user_data["cache"]
    message = query.message
    message.edit_reply_markup()

    if len(user_data["cart"]) == 0:
        message.reply_text(
            text="Ваша корзина пуста.",
            reply_markup=keyboards.order_action_keyboard(empty_cart=True)
        )
        return

    message.reply_text("Корзина сформирована.")
    user = User.get(id=query.from_user.id)

    if user.phone:
        message.reply_text(
            text=f"В прошлом заказе вы указывали номер:\n<code>{user.phone}</code>\n"
                 f"Использовать его в этом заказе?",
            reply_markup=keyboards.phone_keyboard,
        )
    else:
        message.reply_text("Введите ваш номер телефона или отправьте контакт.")

    return PHONE


def incorrect_phone(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Пожалуйста, введите корректный номер телефона. \n"
        "Он нужен, чтобы связаться с вами в случае возникновения затруднений.")


def enter_new_phone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    query.message.reply_text("Введите новый номер телефона или отправьте контакт.")
    user = User.get(id=query.from_user.id)
    user.phone = ""
    user.save()


def use_last_phone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    user = User.get(id=query.from_user.id)

    return to_address(query.message, user)


def get_phone(update: Update, context: CallbackContext):
    message = update.message
    phone = message.contact.phone_number if message.contact else message.text

    if len(phone) == 10:
        phone = "+7" + phone
    elif len(phone) == 11:
        phone = "+" + phone

    user = User.get(id=message.from_user.id)
    user.phone = phone
    user.save()

    return to_address(message, user)


def to_address(message: Message, user: User):
    if user.address:
        message.reply_text(
            text=f"В прошлом заказе вы указывали адрес:\n<code>{user.address}</code>\n"
                 f"Использовать его в этом заказе?",
            reply_markup=keyboards.address_keyboard,
        )
    else:
        message.reply_text("Введите адрес доставки или пришлите локацию.")

    return ADDRESS


def enter_new_address(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    query.message.reply_text("Введите новый адрес или отправьте локацию.")

    user = User.get(id=query.from_user.id)
    user.address = ""
    user.save()


def use_last_address(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    user = User.get(id=query.from_user.id)

    return validate_order(query, user, context.user_data)


def get_address(update: Update, context: CallbackContext):
    message = update.message

    if message.location:
        address = f"{message.location.latitude}, {message.location.longitude}"
    else:
        address = message.text

    user = User.get(id=message.from_user.id)
    user.address = address
    user.save()

    return validate_order(message, user, context.user_data)


def format_items(products: List[Product]):
    positions = "".join([f"- {product}\n" for product in products])
    cost = sum([product.price for product in products])

    return f"Позиции меню:\n{positions}\nСумма: <b>{cost}</b> р."


def validate_order(update: Union[Message, CallbackQuery], user: User, user_data: dict):
    message = update if isinstance(update, Message) else update.message
    products: List[Product] = user_data["cart"]
    positions = format_items(products)

    text = (
        f"{update.from_user.full_name}, Ваш заказ\n\n"
        f"Телефон: <code>{user.phone}</code>\n"
        f"Адрес: <code>{user.address}</code>\n\n"
        f"{positions}"
    )

    message.reply_text(
        text=text,
        reply_markup=keyboards.order_action_keyboard(),
    )

    return CONFIRM


def order_action(update: Update, context: CallbackContext):
    query = update.callback_query
    query.message.edit_reply_markup()
    action = query.data

    if action == "user:confirm":
        return create_order(query, context.user_data)
    elif action == "user:reorder":
        return new_order(update, context)
    elif action == "user:cancel":
        return cancel_order(update, context)


def create_order(query: CallbackQuery, user_data: dict):
    user = User.get(id=query.from_user.id)

    order: Order = Order.create(
        status="подтверждение",
        user=user,
        address=user.address,
        phone=user.phone,
        created=datetime.now(),
    )

    products = user_data["cart"]
    for product in products:
        OrderItem.create(
            order=order,
            product=product,
        )

    message = query.message
    message.reply_text(f"Спасибо! Ваш заказ с номером <code>#{order.id}</code> принят в обработку.\n\n"
                       f"Вам будут приходить уведомления об изменении его статуса.")
    user_data.clear()

    admins: List[User] = User.select().where(User.status == "admin")
    positions = format_items(products)
    text = (
        f"Новый заказ <code>#{order.id}</code>\n\n"
        f"Пользователь: {str(user)}\n"
        f"Телефон: <code>{user.phone}</code>\n"
        f"Адрес: <code>{user.address}</code>\n\n"
        f"{positions}"
    )
    # TODO: вынести в Order.format(self)
    # TODO: получение этого заказ через команду

    for admin in admins:
        message.bot.send_message(
            chat_id=admin.id,
            text=text,
            reply_markup=approve_keyboard(order.id),
        )

    return ConversationHandler.END


def rate_order(update: Update, context: CallbackContext):
    query = update.callback_query
    data = re.match(r"user:rate:(\d+):(\d+)", query.data)
    rate = int(data.group(1))
    order_id = int(data.group(2))

    order: Order = Order.get(id=order_id)
    order.rate = rate
    order.save()

    if 1 <= rate <= 3:
        query.answer("Мы сожалеем. Расскажите, что вам не понравилось?")
    elif rate == 4:
        query.answer("Чего не хватило до идеала?")
    elif rate == 5:
        query.answer("Рады стараться для вас!")

    query.edit_message_reply_markup(
        reply_markup=keyboards.feedback_order_keyboard(order_id),
    )
    query.message.reply_text("Спасибо за заказ! Ждем вас еще!")


def feedback_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    query.message.reply_text(
        text="Ваш отзыв очень важен для нас.\n\n"
             "О чем можно написать:\n"
             "- разнообразие меню\n"
             "- качество блюд\n"
             "- скорость доставки\n\n"
             "Кроме того, вы можете прислать фотографию вашего заказа."
    )
    query.message.reply_text(
        text="Отправьте необходимые сообщения и вложения, а затем "
             "нажмите кнопку <b>Отправить отзыв</b>\n\n"
             "Для отмены введите /cancel",
        reply_markup=keyboards.create_feedback_keyboard,
    )

    order_id = int(re.match(r"user:feedback:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    context.user_data["feedback"] = {
        "order": order,
        "text": [],
        "attachments": [],
    }

    return FEEDBACK


def get_feedback(update: Update, context: CallbackContext):
    feedback: dict = context.user_data["feedback"]
    message = update.message

    if message.photo:
        feedback["attachments"].append(message.photo[-1].file_id)
        message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
    elif message.text:
        feedback["text"].append(message.text)
        message.reply_chat_action(ChatAction.TYPING)


def create_feedback(update: Update, context: CallbackContext):
    update.callback_query.edit_message_reply_markup()
    update.callback_query.message.reply_text("Спасибо за подробный отзыв, мы учтем ваши пожелания!")

    feedback: dict = context.user_data["feedback"]
    order: Order = feedback["order"]
    order.feedback = ".\n".join(feedback["text"])
    order.attachments = ", ".join(feedback["attachments"])
    order.save()

    admins: List[User] = User.select().where(User.status == "admin")
    media = [InputMediaPhoto(photo) for photo in feedback["attachments"]]
    context.user_data.clear()

    for admin in admins:
        context.bot.send_message(
            chat_id=admin.id,
            text=f"Новый отзыв для заказа <code>#{order.id}</code>\n\n"
                 f"{order.feedback}",
        )

        if media:
            context.bot.send_media_group(
                chat_id=admin.id,
                media=media,
            )

        # TODO: Кнопки: Открыть заказ, Обратная связь

    return ConversationHandler.END


def cancel_feedback(update: Update, context: CallbackContext):
    update.message.reply_text("Отзыв отменен.")
    context.user_data.clear()

    return ConversationHandler.END


def register(dp: Dispatcher):
    order_handler = ConversationHandler(
        entry_points=[
            CommandHandler("order", new_order),
            MessageHandler(Filters.regex(re.compile(r".*(новый|заказ).*", re.IGNORECASE)), new_order),
        ],
        states={
            MAIN_DISH: [
                CallbackQueryHandler(pattern=r"user:index:\w+", callback=switch_product),
                CallbackQueryHandler(pattern=r"user:cart:\d+", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"user:next_state", callback=ask_snack),
            ],
            SNACK: [
                CallbackQueryHandler(pattern=r"user:index:\w+", callback=switch_product),
                CallbackQueryHandler(pattern=r"user:cart:\d+", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"user:next_state", callback=ask_drink),
            ],
            DRINK: [
                CallbackQueryHandler(pattern=r"user:index:\w+", callback=switch_product),
                CallbackQueryHandler(pattern=r"user:cart:\d+", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"user:next_state", callback=complete_cart),
                CallbackQueryHandler(pattern=r"user:(reorder|cancel)", callback=order_action),
            ],
            PHONE: [
                MessageHandler(Filters.entity(MessageEntity.PHONE_NUMBER) | Filters.contact, get_phone),
                CallbackQueryHandler(pattern=r"user:last_phone", callback=use_last_phone),
                CallbackQueryHandler(pattern=r"user:new_phone", callback=enter_new_phone),
                MessageHandler(Filters.text & ~Filters.command & ~cancel_filter, incorrect_phone),
            ],
            ADDRESS: [
                MessageHandler((Filters.text & ~Filters.command & ~cancel_filter) | Filters.location, get_address),
                CallbackQueryHandler(pattern=r"user:last_address", callback=use_last_address),
                CallbackQueryHandler(pattern=r"user:new_address", callback=enter_new_address),
            ],
            CONFIRM: [
                CallbackQueryHandler(pattern=r"user:(confirm|reorder|cancel)", callback=order_action),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_order),
            MessageHandler(cancel_filter, cancel_order),
        ],
    )

    dp.add_handler(order_handler)
    dp.add_handler(CallbackQueryHandler(pattern=r"user:rate:\d+", callback=rate_order))

    feedback_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=r"user:feedback:\d+", callback=feedback_order),
        ],
        states={
            FEEDBACK: [
                MessageHandler((Filters.text & ~Filters.command & ~cancel_filter) | Filters.photo, get_feedback),
                CallbackQueryHandler(pattern=r"user:feedback:create", callback=create_feedback),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_feedback),
            MessageHandler(cancel_filter, cancel_feedback),
        ],
    )

    dp.add_handler(feedback_handler)
