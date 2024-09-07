import datetime

# 날짜와 시간을 "YYYY.MM.DD.HHMMSS" 형식으로 포맷
__version__ = datetime.datetime.now().strftime("%Y.%m.%d.%H%M%S")
VERSION = __version__
