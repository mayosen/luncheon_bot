from telegram import BotCommand
from telegram.ext import Updater

from config import ADMIN


def set_default_commands(updater: Updater):
    updater.bot.set_my_commands(
        [
            BotCommand("profile", "Ваш профиль"),
            BotCommand("order", "Сделать заказ"),
            BotCommand("history", "История заказов"),
        ]
    )


def on_startup_notification(updater: Updater):
    updater.bot.send_message(chat_id=ADMIN, text="<i>Бот запущен.</i>")
