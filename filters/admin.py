from telegram import Message
from telegram.ext import MessageFilter

from config import ADMINS


class IsAdmin(MessageFilter):
    def filter(self, message: Message):
        return message.from_user.id in ADMINS
