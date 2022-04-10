from . import switch
from . import orders

from loader import dp


switch.register(dp)
orders.register(dp)
