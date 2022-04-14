from typing import List

from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.ext import MessageHandler

from filters import is_admin

from database.models import Product


def register(dp: Dispatcher):
    pass
