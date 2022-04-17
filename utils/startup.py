from telegram import BotCommand, BotCommandScope
from telegram import Bot

from database.api import get_admins


def set_default_commands(bot: Bot):
    bot.set_my_commands(
        [
            BotCommand("order", "Сделать заказ"),
            BotCommand("cancel", "Отменить заказ"),
            BotCommand("me", "Ваш профиль"),
        ]
    )


def on_startup_notification(bot: Bot):
    admins = get_admins()
    for admin in admins:
        bot.send_message(chat_id=admin.id, text="<i>Бот запущен.</i>")
