import re
from typing import List, Union, Dict

from telegram import Update, Message, MessageEntity, CallbackQuery, InputMediaPhoto
from telegram.ext import Dispatcher, CallbackContext, Filters
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, ConversationHandler

from database.models import User, Product, Order, OrderItem
from database.api import check_user, get_admins, get_order_products
from filters.cancel import cancel_filter
from handlers.users.profile import incorrect_phone, update_phone, update_address
from keyboards.admin import approve_keyboard
from keyboards.feedback import feedback_order_keyboard
import keyboards.order as keyboards
from utils.startup import clean_unprocessed_orders
from utils.formatting import format_order
from utils.literals import OrderStates, OrderState

MAIN_DISH, SNACK, DRINK, PHONE, ADDRESS, CONFIRM = range(6)


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

    admins = get_admins()
    if not admins:
        message.reply_text("Извините, на данный момент нет активных администраторов, которые могут "
                           "принять ваш заказ.\n\nПожалуйста, вернитесь позднее.")
        return ConversationHandler.END

    message.reply_text(
        "Сборка заказа:\n"
        "- основное блюдо\n"
        "- закуска\n"
        "- напиток\n\n"
        "/cancel - отменить заказ"
    )
    process_state(to_process, OrderStates.MAIN_DISH, context.user_data)

    return MAIN_DISH


def repeat_order(update: Update, context: CallbackContext):
    query = update.callback_query
    order_id = int(re.match(r"user:reorder:(\d+)", query.data).group(1))
    order = Order.get(id=order_id)
    products = get_order_products(order)
    context.user_data["cart"] = products
    query.message.reply_text("Введите /cancel для отмены заказа.")

    return complete_cart(update, context)


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
        query.answer()
        return
    else:
        new_index = int(data)

    user_data = context.user_data
    products = user_data["cache"]
    product = products[new_index]
    state: OrderState = user_data["state"]

    query.message.edit_media(
        media=InputMediaPhoto(
            media=product.photo,
            caption=f"{product.title}\nЦена: {product.price} р.",
        ),
        reply_markup=keyboards.product_keyboard(state.next_category, new_index, len(products)),
    )


def process_state(update: Union[Message, CallbackQuery], state: OrderState, user_data: Dict):
    message = update.message if isinstance(update, CallbackQuery) else update

    products: List[Product] = Product.select().where(Product.category == state.category)
    user_data["cache"] = products
    user_data["state"] = state

    index = 0
    product = products[index]

    message.reply_text(f"Выберите {state.choose}.")
    message.reply_photo(
        photo=product.photo,
        caption=f"{product.title}\nЦена: {product.price} р.",
        reply_markup=keyboards.product_keyboard(state.next_category, index, len(products)),
    )


def add_to_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    index = int(re.match(r"user:cart:(\w+)", data).group(1))
    user_data = context.user_data
    product: Product = user_data["cache"][index]
    user_data["cart"].append(product)
    query.answer(f"Добавлено в корзину:\n{product}")


def ask_snack(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    process_state(query, OrderStates.SNACK, context.user_data)

    return SNACK


def ask_drink(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_reply_markup()
    process_state(query, OrderStates.DRINK, context.user_data)

    return DRINK


def complete_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data

    match = re.match(r"user:cart:(\d+)", query.data)
    if match:
        index = int(match.group(1))
        product = user_data["cache"][index]
        user_data["cart"].append(product[index])

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
    user = update_phone(message)

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
    user = update_address(message)

    return validate_order(message, user, context.user_data)


def validate_order(update: Union[Message, CallbackQuery], user: User, user_data: Dict):
    message = update if isinstance(update, Message) else update.message
    products: List[Product] = user_data["cart"]

    text = (
        f"{update.from_user.full_name}, Ваш заказ\n\n" + format_order(user, products)
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
        return create_order(query, context)
    elif action == "user:reorder":
        return new_order(update, context)
    elif action == "user:cancel":
        return cancel_order(update, context)


def check_unprocessed_order(context: CallbackContext):
    order_id = context.job.context
    order = Order.get(id=order_id)
    if isinstance(order, Order) and order.status == "подтверждение":
        clean_unprocessed_orders(context.bot, order)


def create_order(query: CallbackQuery, context: CallbackContext):
    user = User.get(id=query.from_user.id)

    order: Order = Order.create(
        status="подтверждение",
        user=user,
        address=user.address,
        phone=user.phone,
    )

    products = context.user_data["cart"]
    for product in products:
        OrderItem.create(
            order=order,
            product=product,
        )

    context.user_data.clear()
    message = query.message
    message.reply_text(
        f"Спасибо! Ваш заказ с номером <code>#{order.id}</code> принят в обработку.\n\n"
        f"Вам будут приходить уведомления об изменении его статуса."
    )
    context.job_queue.run_once(check_unprocessed_order, 120, context=order.id)

    admins = get_admins()
    text = (
        f"Новый заказ <code>#{order.id}</code>\n\n"
        f"Пользователь: {str(user)}\n"
        + format_order(user, products)
    )

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
    order_id = int(data.group(1))
    rate = int(data.group(2))

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
        reply_markup=feedback_order_keyboard(order_id),
    )
    query.message.reply_text("Спасибо за заказ! Ждем вас еще!")


def register(dp: Dispatcher):
    order_handler = ConversationHandler(
        entry_points=[
            CommandHandler("order", new_order),
            MessageHandler(Filters.regex(re.compile(r".*(новый|заказ).*", re.IGNORECASE)), new_order),
            CallbackQueryHandler(pattern=r"^user:reorder:\d+$", callback=repeat_order),
        ],
        states={
            MAIN_DISH: [
                CallbackQueryHandler(pattern=r"^user:index:(\d+|pass)$", callback=switch_product),
                CallbackQueryHandler(pattern=r"^user:cart:\d+$", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"^user:next_state$", callback=ask_snack),
            ],
            SNACK: [
                CallbackQueryHandler(pattern=r"^user:index:(\d+|pass)$", callback=switch_product),
                CallbackQueryHandler(pattern=r"^user:cart:\d+$", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"^user:next_state$", callback=ask_drink),
            ],
            DRINK: [
                CallbackQueryHandler(pattern=r"^user:index:(\d+|pass)$", callback=switch_product),
                CallbackQueryHandler(pattern=r"^user:cart:\d+$", callback=add_to_cart),
                CallbackQueryHandler(pattern=r"^user:next_state$", callback=complete_cart),
                CallbackQueryHandler(pattern=r"^user:(reorder|cancel)$", callback=order_action),
            ],
            PHONE: [
                MessageHandler(Filters.entity(MessageEntity.PHONE_NUMBER) | Filters.contact, get_phone),
                CallbackQueryHandler(pattern=r"^user:last_phone$", callback=use_last_phone),
                CallbackQueryHandler(pattern=r"^user:new_phone$", callback=enter_new_phone),
                MessageHandler(Filters.text & ~Filters.command & ~cancel_filter, incorrect_phone),
            ],
            ADDRESS: [
                MessageHandler((Filters.text & ~Filters.command & ~cancel_filter) | Filters.location, get_address),
                CallbackQueryHandler(pattern=r"^user:last_address$", callback=use_last_address),
                CallbackQueryHandler(pattern=r"^user:new_address$", callback=enter_new_address),
            ],
            CONFIRM: [
                CallbackQueryHandler(pattern=r"^user:(confirm|reorder|cancel)$", callback=order_action),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_order),
            MessageHandler(cancel_filter, cancel_order),
        ],
    )

    dp.add_handler(order_handler)
    dp.add_handler(CallbackQueryHandler(pattern=r"^user:rate:\d+:\d+$", callback=rate_order))
