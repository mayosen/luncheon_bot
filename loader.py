import logging

from telegram import ParseMode
from telegram.ext import Updater, Defaults

from config import TOKEN


logging.basicConfig(
    format=u"[%(levelname)s] %(name)s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)

defaults = Defaults(parse_mode=ParseMode.HTML)
updater = Updater(TOKEN, defaults=defaults)
dp = updater.dispatcher
