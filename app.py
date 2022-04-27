from telegram.ext import CallbackContext

from loader import updater
import handlers
import utils.startup as utils


def on_startup(context: CallbackContext):
    bot = context.bot
    utils.set_default_commands(bot)
    utils.on_startup_notification(bot)
    utils.clean_unprocessed_orders(bot)


if __name__ == "__main__":
    updater.job_queue.run_once(on_startup, 0)
    updater.start_polling(drop_pending_updates=True)
    updater.idle()
