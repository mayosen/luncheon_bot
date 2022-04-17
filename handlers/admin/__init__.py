from . import login
from . import orders
from . import helpers

from loader import dp


login.register(dp)
orders.register(dp)
helpers.register(dp)
