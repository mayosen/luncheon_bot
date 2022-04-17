import re
from telegram.ext import Filters

cancel_filter = Filters.regex(re.compile(r".*(отмена|стоп).*", re.IGNORECASE))
