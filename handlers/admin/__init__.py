from . import login
from . import orders
from . import commands
from . import helpers

from loader import dp


login.register(dp)
orders.register(dp)
commands.register(dp)
helpers.register(dp)
