import time
import sqlite3
import pandas as pd
import logging
from datetime import datetime
from alpaca_trade_api.rest import REST, TimeFrame


API_KEY = "PKYWI7S1X0M9H8TMDF6E"
API_SECRET = "ViEpeMhdQoeWUR6cwJjdVkGM9fwS9fN7VxiFFHQIw"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)


logging.basicConfig(filename="trading_bot.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def log_trade(symbol, side, price):
    """Logs trade data to a file."""
    log_message = f"TRADE EXECUTED: {side.upper()} {symbol} at ${price}"
    print(log_message)
    logging.info(log_message)


def log_error(error_message):
    """Logs errors to a file."""
    print(f"⚠️ Error: {error_message}")
    logging.error(error_message)


# ✅ Function to check if market is open
def is_market_open():
    """Checks if the market is currently open using Alpaca API."""
    try:
        clock = api.get_clock()
        return clock.is_open
    except Exception as e:
        log_error(f"Error checking market status: {e}")
        return False


# ✅ Function to fetch live stock price
def fetch_live_price(symbol):
    """Fetches the latest live price for a stock symbol, handling market closures."""
    if not is_market_open():
        print("⏳ Market is closed. Bot will wait 5 minutes before retrying...")
        time.sleep(300)  # ✅ Corrected sleep function
        return None

    try:
        trade = api.get_last_trade(symbol)
        return trade.price if hasattr(trade, "price") else None
    except Exception as e:
        log_error(f"Error fetching live price for {symbol}: {e}")
        return None


# ✅ Function to place trades
def place_paper_trade(symbol, qty, side, stop_loss=None, take_profit=None):
    """Places a simulated trade in Alpaca's paper trading account."""
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type="market",
            time_in_force="gtc"
        )
        log_trade(symbol, side, stop_loss if stop_loss else take_profit)
        return order
    except Exception as e:
        log_error(f"Error placing trade for {symbol}: {e}")
        return None


# ✅ Function to trade multiple stocks
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
TRADE_QUANTITY = 1
CHECK_INTERVAL = 60  # Check every 60 seconds

print("🚀 Automated Trading Bot Started")

while True:
    try:
        if not is_market_open():
            print("⏳ Market is closed. Bot will wait 5 minutes before retrying...")
            time.sleep(300)  # ✅ Corrected sleep function
            continue

        for symbol in STOCKS:
            live_price = fetch_live_price(symbol)
            if live_price is None:
                continue

            place_paper_trade(symbol, TRADE_QUANTITY, "buy")

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        time.sleep(10)  # ✅ Corrected sleep function
