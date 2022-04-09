from . import admin
from . import other

from loader import dp


if __name__ == "handlers":
    # admin.register(dp)
    other.register(dp)
