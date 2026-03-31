














"""
Utility functions for the trading bot
Includes: logging setup, risk management, order helpers, notifications, etc.
"""

import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

import ccxt
import pandas as pd

from config import SYMBOL, TAKE_PROFIT, STOP_LOSS, AMOUNT


def setup_logging(log_file: str = "trading_bot.log") -> logging.Logger:
    """Setup logging configuration"""
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(f"logs/{log_file}", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"Trading Bot Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Trading Pair: {SYMBOL}")
    logger.info("=" * 60)
    
    return logger


def calculate_position_size(balance: Dict, price: float, risk_percent: float = 1.0) -> float:
    """
    Calculate safe position size based on available balance and risk percentage
    """
    try:
        # Get USDT balance (or quote currency)
        quote_currency = SYMBOL.split('/')[1]
        available = balance.get('free', {}).get(quote_currency, 0)
        
        if available <= 0:
            return 0.0
            
        # Risk only X% of available balance per trade
        max_risk_amount = available * (risk_percent / 100)
        position_value = min(max_risk_amount * 5, available * 0.1)  # Max 10% of balance per trade
        
        amount = position_value / price
        
        # Round down to safe decimal places
        return round(amount, 6)
        
    except Exception:
        return AMOUNT  # Fallback to config amount


def get_current_balance(exchange: ccxt.Exchange, symbol: str) -> Dict:
    """Fetch and format current balance"""
    try:
        balance = exchange.fetch_balance()
        base = symbol.split('/')[0]
        quote = symbol.split('/')[1]
        
        base_free = balance.get('free', {}).get(base, 0)
        quote_free = balance.get('free', {}).get(quote, 0)
        
        return {
            'base': base,
            'quote': quote,
            'base_free': round(base_free, 6),
            'quote_free': round(quote_free, 2),
            'total_usd_value': round(quote_free + (base_free * exchange.fetch_ticker(symbol)['last']), 2)
        }
    except Exception as e:
        logging.error(f"Failed to fetch balance: {e}")
        return {}


def calculate_pnl(entry_price: float, current_price: float, side: str) -> Tuple[float, float]:
    """Calculate unrealized PnL and percentage"""
    if side.lower() == 'buy' or side.lower() == 'long':
        pnl = current_price - entry_price
        pnl_pct = (pnl / entry_price) * 100
    else:
        pnl = entry_price - current_price
        pnl_pct = (pnl / entry_price) * 100
    
    return round(pnl, 4), round(pnl_pct, 2)


def check_take_profit_stop_loss(entry_price: float, current_price: float, side: str) -> str:
    """Check if TP or SL is hit"""
    if side.lower() in ['buy', 'long']:
        if current_price >= entry_price * (1 + TAKE_PROFIT):
            return 'take_profit'
        elif current_price <= entry_price * (1 - STOP_LOSS):
            return 'stop_loss'
    else:  # short
        if current_price <= entry_price * (1 - TAKE_PROFIT):
            return 'take_profit'
        elif current_price >= entry_price * (1 + STOP_LOSS):
            return 'stop_loss'
    return None


def send_telegram_notification(message: str, bot_token: str = None, chat_id: str = None):
    """Send notification to Telegram (optional)"""
    if not bot_token or not chat_id:
        return False
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': f"🟢 Trading Bot\n\n{message}",
            'parse_mode': 'HTML'
        }
        requests.post(url, json=payload, timeout=10)
        return True
    except Exception as e:
        logging.warning(f"Telegram notification failed: {e}")
        return False


def format_order_message(signal: str, price: float, amount: float, reason: str = "") -> str:
    """Format nice message for logs and notifications"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if signal == 'buy':
        emoji = "🟢"
        action = "BUY"
    elif signal == 'sell':
        emoji = "🔴"
        action = "SELL"
    else:
        emoji = "⚪"
        action = signal.upper()
    
    msg = f"{emoji} {action} Signal\n"
    msg += f"Time: {timestamp}\n"
    msg += f"Pair: {SYMBOL}\n"
    msg += f"Price: {price:.4f}\n"
    msg += f"Amount: {amount:.6f}\n"
    
    if reason:
        msg += f"Reason: {reason}\n"
    
    return msg


# Optional: Simple rate limiter
class RateLimiter:
    def __init__(self, calls_per_minute: int = 30):
        self.calls_per_minute = calls_per_minute
        self.timestamps = []
    
    def can_call(self) -> bool:
        now = time.time()
        # Remove calls older than 60 seconds
        self.timestamps = [t for t in self.timestamps if now - t < 60]
        
        if len(self.timestamps) < self.calls_per_minute:
            self.timestamps.append(now)
            return True
        return False


# For future use: Portfolio tracking
def log_portfolio_snapshot(exchange: ccxt.Exchange, symbol: str, logger: logging.Logger):
    """Log current portfolio status"""
    try:
        balance = get_current_balance(exchange, symbol)
        ticker = exchange.fetch_ticker(symbol)
        
        logger.info(f"Portfolio Snapshot | "
                    f"{balance.get('base', '')}: {balance.get('base_free', 0)} | "
                    f"{balance.get('quote', '')}: {balance.get('quote_free', 0)} | "
                    f"Price: {ticker['last']:.4f} | "
                    f"Total ~${balance.get('total_usd_value', 0)}")
    except Exception as e:
        logger.error(f"Failed to log portfolio: {e}")
