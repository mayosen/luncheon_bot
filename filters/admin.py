from telegram import Message
from telegram.ext import MessageFilter

from database.api import get_admins


class IsAdmin(MessageFilter):
    def filter(self, message: Message):
        admins = get_admins()
        return message.from_user.id in [admin.id for admin in admins]
