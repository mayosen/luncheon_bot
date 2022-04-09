from telegram import BotCommand
from telegram.ext import Updater

from config import ADMINS


def set_default_commands(updater: Updater):
    updater.bot.set_my_commands(
        [
            BotCommand("order", "Новый заказ"),
            BotCommand("me", "Ваш профиль"),
        ]
    )


def on_startup_notification(updater: Updater):
    admin = ADMINS[0]
    updater.bot.send_message(chat_id=admin, text="<i>Бот запущен.</i>")
