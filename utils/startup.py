from telegram import BotCommand
from telegram import Bot

from database.api import get_admins

DEFAULT_COMMANDS = [
    BotCommand("order", "Сделать заказ"),
    BotCommand("cancel", "Отменить действие"),
    BotCommand("me", "Ваш профиль"),
]


def set_default_commands(bot: Bot):
    bot.set_my_commands(DEFAULT_COMMANDS)


def on_startup_notification(bot: Bot):
    admins = get_admins()
    for admin in admins:
        bot.send_message(chat_id=admin.id, text="<i>Бот запущен.</i>")
