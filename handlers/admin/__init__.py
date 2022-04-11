from . import switch
from . import orders
from . import helpers

from loader import dp


switch.register(dp)
orders.register(dp)
helpers.register(dp)
