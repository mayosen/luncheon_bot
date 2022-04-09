from telegram import Message
from telegram.ext import MessageFilter

from config import ADMIN


class IsAdmin(MessageFilter):
    def filter(self, message: Message):
        return message.from_user.id == ADMIN
