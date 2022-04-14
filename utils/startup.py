from telegram import BotCommand, BotCommandScope
from telegram import Bot

from config import ADMINS


def set_default_commands(bot: Bot):
    bot.set_my_commands(
        [
            BotCommand("order", "Сделать заказ"),
            BotCommand("cancel", "Отменить заказ"),
            BotCommand("me", "Ваш профиль"),
        ]
    )


def on_startup_notification(bot: Bot):
    admin = ADMINS[0]
    bot.send_message(chat_id=admin, text="<i>Бот запущен.</i>")
