from telegram import Bot

from loader import updater
import handlers
from utils.startup import on_startup_notification, set_default_commands


def on_startup(bot: Bot):
    set_default_commands(bot)
    on_startup_notification(bot)


if __name__ == "__main__":
    try:
        on_startup(updater.bot)
        updater.start_polling(drop_pending_updates=True)
    finally:
        pass
