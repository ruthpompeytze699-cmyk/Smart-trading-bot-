



import ccxt
import pandas as pd
import pandas_ta as ta  # pip install pandas-ta if no ta-lib

def get_ohlcv(exchange, symbol, timeframe, limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def generate_signal(df):
    df['sma_short'] = ta.sma(df['close'], length=10)
    df['sma_long'] = ta.sma(df['close'], length=30)
    
    if df['sma_short'].iloc[-1] > df['sma_long'].iloc[-1] and df['sma_short'].iloc[-2] <= df['sma_long'].iloc[-2]:
        return 'buy'
    elif df['sma_short'].iloc[-1] < df['sma_long'].iloc[-1] and df['sma_short'].iloc[-2] >= df['sma_long'].iloc[-2]:
        return 'sell'
    return None
