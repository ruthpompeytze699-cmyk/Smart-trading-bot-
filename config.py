





import os
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_ID = os.getenv('EXCHANGE', 'binance')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Bot settings
SYMBOL = 'BTC/USDT'
TIMEFRAME = '5m'          # 1m, 5m, 15m, 1h, etc.
AMOUNT = 0.001            # Amount to trade (in base currency)
TAKE_PROFIT = 0.02        # 2%
STOP_LOSS = 0.01          # 1%

# Strategy parameters (example: SMA crossover)
SHORT_WINDOW = 10
LONG_WINDOW = 30
