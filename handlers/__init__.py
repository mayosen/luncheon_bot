from . import admin

from . import users

from . import other

from loader import dp


if __name__ == "handlers":
    # admin.register(dp)
    users.register(dp)
    other.register(dp)
