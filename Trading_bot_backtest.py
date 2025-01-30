import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
import logging

# ✅ Paper Trading API Setup (Replace with real API keys)
API_KEY = "PKK7QJC6RD055K9PTKIO"
API_SECRET = "D8EiDM5OCN3sCAHjf8GxvdfGCfLU4BcNU7FsQz41"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

# ✅ Define stocks and timeframe for backtesting
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
START_DATE = "2023-06-01"  # Start date for backtest
END_DATE = "2023-12-31"  # End date for backtest
TRADE_QUANTITY = 1  # 1 share per trade
INITIAL_BALANCE = 10000  # Starting cash balance

# ✅ Set up logging
logging.basicConfig(filename="backtest.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ✅ Function to fetch historical data
def fetch_historical_data(symbol):
    """Fetches historical daily stock data from Alpaca."""
    try:
        bars = api.get_bars(symbol, TimeFrame.Day, start=START_DATE, end=END_DATE).df
        return bars
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


# ✅ Function to simulate trading strategy
def simulate_trading():
    portfolio_value = INITIAL_BALANCE  # Starting balance
    holdings = {symbol: 0 for symbol in STOCKS}  # Track holdings
    cash_balance = portfolio_value  # Start with full cash
    trade_log = []

    for symbol in STOCKS:
        df = fetch_historical_data(symbol)
        if df.empty:
            continue

        # ✅ More aggressive moving averages
        df["20_MA"] = df["close"].rolling(window=20).mean()
        df["100_MA"] = df["close"].rolling(window=100).mean()

        for i in range(1, len(df)):
            short_ma = df["20_MA"].iloc[i]
            long_ma = df["100_MA"].iloc[i]

            # ✅ Buy signal: 20-day MA crosses above 100-day MA (More frequent trades)
            if short_ma > long_ma and holdings[symbol] == 0 and cash_balance >= df["close"].iloc[i] * TRADE_QUANTITY:
                buy_price = df["close"].iloc[i]
                holdings[symbol] += TRADE_QUANTITY
                cash_balance -= buy_price * TRADE_QUANTITY
                trade_log.append({"Date": df.index[i], "Symbol": symbol, "Action": "BUY", "Price": buy_price})
                logging.info(f"BUY {symbol} at ${buy_price}")

            # ✅ Partial Sell: Sell 50% instead of full
            elif short_ma < long_ma and holdings[symbol] > 0:
                sell_qty = holdings[symbol] // 2  # Sell half of holdings
                sell_price = df["close"].iloc[i]
                cash_balance += sell_price * sell_qty
                holdings[symbol] -= sell_qty
                trade_log.append({"Date": df.index[i], "Symbol": symbol, "Action": "SELL", "Price": sell_price,
                                  "Quantity": sell_qty})
                logging.info(f"SELL {symbol} at ${sell_price} (Quantity: {sell_qty})")

    # ✅ Calculate final portfolio value
    final_value = cash_balance + sum(
        holdings[symbol] * fetch_historical_data(symbol)["close"].iloc[-1] for symbol in STOCKS if
        not fetch_historical_data(symbol).empty)
    return trade_log, INITIAL_BALANCE, final_value


# ✅ Run simulation
trade_log, starting_balance, final_balance = simulate_trading()

# ✅ Save trade log to CSV
trade_df = pd.DataFrame(trade_log)
trade_df.to_csv("backtest_results.csv", index=False)

# ✅ Display results
profit_or_loss = final_balance - starting_balance
profit_or_loss_percentage = (profit_or_loss / starting_balance) * 100

print(f"Starting Portfolio Value: ${starting_balance:.2f}")
print(f"Final Portfolio Value: ${final_balance:.2f}")
print(f"Net Profit/Loss: ${profit_or_loss:.2f} ({profit_or_loss_percentage:.2f}%)")

print("Backtest complete! Results saved to backtest_results.csv.")
