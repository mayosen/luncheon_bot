from telegram.ext import Updater

from loader import updater
import filters, handlers

from utils.startup import on_startup_notification, set_default_commands


def on_startup(upd: Updater):
    set_default_commands(upd)
    on_startup_notification(upd)


if __name__ == "__main__":
    try:
        # TODO: Connect DB
        on_startup(updater)
        updater.start_polling(drop_pending_updates=True)
    finally:
        # TODO: Close DB
        pass
