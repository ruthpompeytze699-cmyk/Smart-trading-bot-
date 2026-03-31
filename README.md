

# My Trading Bot

A simple, extensible cryptocurrency trading bot built with Python and CCXT.

## Features
- Supports 100+ exchanges via CCXT
- SMA Crossover strategy (easy to customize)
- Dry-run mode
- Logging and error handling

## Installation
```bash
git clone https://github.com/yourusername/my-trading-bot.git
cd my-trading-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
