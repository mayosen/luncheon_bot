from . import start
from . import profile
from . import order
from . import feedback
from . import other

from loader import dp


start.register(dp)
profile.register(dp)
order.register(dp)
feedback.register(dp)
other.register(dp)
