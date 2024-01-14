# dmarket_bot
Bot for automatic trading on dmarket 

### Setup:

- git clone https://github.com/Cfomodz/dmarket_bot.git
- cd dmarket_bot
- Create a virtual environment python3 -m venv venv
- Activate the virtual environment . venv/bin/activate
- pip install -r requirements.txt
- Create a file `credentials.py` in the root directory with the following content:

```python
PUBLIC_KEY = "your public api key"
SECRET_KEY = "your secret api key"
```

- The bot is being run using `main.py`

## Features:

- Supports all games available on dmarket.
- Automatic analysis of the skins/items for each game
- Placing orders which are determined by 15 different parameters
- Automatic setting of skins/items for sale after purchase. Adjusting of prices in accordance with the settings.

## Configuration

All configuration parameters are set in the `config.py` file in the root directory of the bot.

### Detailed description of the configuration:

- `logger_config`- logger configuration
```python
logger_config = {
    "handlers": [
        {"sink": sys.stderr, 'colorize': True, 'level': 'INFO'},
        # {"sink": "log/debug.log", "serialize": False, 'level': 'DEBUG'},
        {"sink": "log/info.log", "serialize": False, 'level': 'INFO'},
    ]
}
logger.configure(**logger_config)
```
`"sink": sys.stderr` - output logs to the console
`"sink": "log/info.log"` - output logs to a file
`'level': 'INFO'` is the level of the logs. Possible settings: `TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR , CRITICAL`. Each level from left to right prohibits the output of lower levels. IF the level `INFO` is set messages with the levels `TRACE, DEBUG` won't be displayed.
- `GAMES = [Games.CS, Games.DOTA, Games.RUST]` - a lisit of games that will be used for trading. Available values: `Games.CS, Games.DOTA, Games.RUST, Games.TF2`
- `PREV_BASE = 60 * 60 * 4` - update the skin database every `PREV_BASE` seconds
- `ORDERS_BASE = 60 * 10`- update the order database `ORDERS_BASE` seconds
- `BAD_ITEMS` - a blacklist of words. If the word is included in the name of the item it won't be bought.

### BuyParams - configuration parameters for placing orders
- `STOP_ORDERS_BALANCE = 1000` - Stop placing orders if the balance is <= 10 dollars more than the minimum order price
- `MIN_AVG_PRICE = 400` - The minimum average price for the last 20 purchases of an item in cents. Items with a lower won't be added to the skin database
- `MAX_AVG_PRICE = 3500` - The maximum average price for the last 20 purchases of an item in cents. Items with a higher price will not be added to the skin database. 
- `FREQUENCY = True` - `PROFIT_PERCENT = 6` or less, and the parameter `GOOD_POINTS_PERCENT = 50` or higher.
- `MIN_PRICE = 300` - minimum price. The order won't be placed below this price
- `MAX_PRICE = 3000` - maximum price. The order won't be placed above this price

- `PROFIT_PERCENT = 7` - 
- `GOOD_POINTS_PERCENT = 50` - the minimum percentage of points in the history of the last 20 sales corresponding to the parameter `PROFIT_PERCENT = 7`. In this case, if less than 50 % of points were sold with a profit of less than 7 %, then an order for such a skin/item won't be placed
- `AVG_PRICE_COUNT = 7` - calculating the average price for the last 7 sales to form the estimated profit
- `ALL_SALES = 100` - the minimum number of sales for the entire period, if sales are below this number, the order won't be placed
- `DAYS_COUNT = 20` - at least `SALE_COUNT = 15` sales for `DAYS_COUNT = 20` days. Selection by popularity
- `SALE_COUNT = 15` - at least `SALE_COUNT = 15` sales for `DAYS_COUNT = 20` days. Selection by popularity
- `LAST_SALE = 2` - last sale is no older than LAST_SALE days ago
- `FIRST_SALE = 15` - first purchase is no later than FIRST_SALE days ago

- `MAX_COUNT_SELL_OFFERS = 30` - The maximum number of items for sale. Above 30 the order won't be placed

- `BOOST_PERCENT = 24` - remove up to 3 points that are 24 % higher than average price
- `BOOST_POINTS = 3` - remove up to 3 points that are 24 % higher than average price

- `MAX_THRESHOLD = 1` - the maximum price increase by MAX_THRESHOLD in % of the current order. The maximum increase in the price of your order from the price of the current first order
- `MIN_THRESHOLD = 3` - the maximum decrease in the price of your order from the price of the current one. Sets the price change boundaries for the order

### SellParams - configuration parameters for selling
- `MIN_PERCENT = 7` - minimum profit percentage
- `MAX_PERCENT = 15` - maximum profit percentage
