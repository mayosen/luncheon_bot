from . import start
from . import profile
from . import order
from . import other

from loader import dp


start.register(dp)
profile.register(dp)
order.register(dp)
other.register(dp)
