import sys
from loguru import logger

from api.schemas import Games
from credentials import PUBLIC_KEY, SECRET_KEY

logger_config = {
    "handlers": [
        {"sink": sys.stderr, 'colorize': True, 'level': 'INFO'},
        {"sink": sys.stderr, "serialize": False, 'level': 'DEBUG'},
        {"sink": "log/info.log", "serialize": False, 'level': 'INFO'},
    ]
}
logger.configure(**logger_config)


API_URL = "https://api.dmarket.com"
API_URL_TRADING = API_URL
# GAMES = [Games.CS, Games.DOTA, Games.RUST]
GAMES = [Games.RUST]
DATABASE_NAME = '/skins.db'

BAD_ITEMS = ['key', 'pin', 'sticker', 'case', 'operation', 'pass', 'capsule', 'package', 'challengers',
            'patch', 'music', 'kit', 'graffiti']


class Timers:
    PREV_BASE = 60 * 60 * 5 # 5 hours
    ORDERS_BASE = 60 * 10


class PrevParams:
    # POPULARITY = 3
    MIN_AVG_PRICE = 92
    MAX_AVG_PRICE = 93


class BuyParams:
    STOP_ORDERS_BALANCE = 100
    FREQUENCY = True
    MIN_PRICE = 50
    MAX_PRICE = 1250

    PROFIT_PERCENT = 5
    GOOD_POINTS_PERCENT = 30
    AVG_PRICE_COUNT = 7

    ALL_SALES = 80
    DAYS_COUNT = 23
    SALE_COUNT = 11
    LAST_SALE = 3  # Last sale no later than LAST_SALE days ago
    FIRST_SALE = 20  # First purchase no later than FIRST_SALE days ago

    MAX_COUNT_SELL_OFFERS = 20

    BOOST_PERCENT = 24
    BOOST_POINTS = 3

    MAX_THRESHOLD = 0.1  # Maximum price increase for MAX_THRESHOLD in percent of the current order
    MIN_THRESHOLD = 3  # Minimum price decrease by MIN_THRESHOLD in percent of the current order


class SellParams:
    MIN_PERCENT = 7
    MAX_PERCENT = 15
