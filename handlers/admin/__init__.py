from . import status
from . import orders

from loader import dp


status.register(dp)
orders.register(dp)
