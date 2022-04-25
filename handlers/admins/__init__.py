from . import login
from . import orders
from . import commands
from . import helpers
from . import errors

from loader import dp


login.register(dp)
orders.register(dp)
commands.register(dp)
helpers.register(dp)
errors.register(dp)
