from . import profile
from . import order
from . import feedback
from . import other

from loader import dp


profile.register(dp)
order.register(dp)
feedback.register(dp)
other.register(dp)
