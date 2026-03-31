









import ccxt
import time
import logging
from config import *
from strategy import get_ohlcv, generate_signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

exchange = getattr(ccxt, EXCHANGE_ID)({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

def main():
    logging.info(f"Starting trading bot for {SYMBOL} on {EXCHANGE_ID}")
    
    while True:
        try:
            df = get_ohlcv(exchange, SYMBOL, TIMEFRAME, limit=100)
            signal = generate_signal(df)
            
            balance = exchange.fetch_balance()
            price = exchange.fetch_ticker(SYMBOL)['last']
            
            if signal == 'buy':
                logging.info("Buy signal detected!")
                # exchange.create_market_buy_order(SYMBOL, AMOUNT)  # Uncomment for live
                print(f"Would buy {AMOUNT} {SYMBOL} at ~{price}")
            
            elif signal == 'sell':
                logging.info("Sell signal detected!")
                # exchange.create_market_sell_order(SYMBOL, AMOUNT)
                print(f"Would sell at ~{price}")
            
            time.sleep(60)  # Check every minute (adjust to timeframe)
            
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
