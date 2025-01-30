import tkinter as tk
from tkinter import ttk
import time
import sqlite3
import pandas as pd
import logging
from datetime import datetime
from alpaca_trade_api.rest import REST, TimeFrame


API_KEY = "your api key"
API_SECRET = "your secret api key"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)


logging.basicConfig(filename="trading_bot.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Function to fetch live stock data
def fetch_live_data():
    """Fetches the latest live trading data for multiple stocks."""
    stock_data = []
    for symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]:
        try:
            trade = api.get_last_trade(symbol)
            price = trade.price if hasattr(trade, "price") else None
            stock_data.append({"symbol": symbol, "price": price, "status": "Active"})
        except Exception as e:
            logging.error(f"Error fetching live price for {symbol}: {e}")
            stock_data.append({"symbol": symbol, "price": "N/A", "status": "Error"})
    return stock_data

# ✅ Function to fetch account portfolio
def fetch_portfolio():
    """Fetches portfolio valuation and holdings from Alpaca."""
    try:
        account = api.get_account()
        portfolio_value = float(account.equity)
        positions = api.list_positions()
        holdings = {pos.symbol: int(pos.qty) for pos in positions}
        return portfolio_value, holdings
    except Exception as e:
        logging.error(f"Error fetching portfolio data: {e}")
        return None, {}

# ✅ GUI Implementation
class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot Monitor")
        self.root.geometry("600x500")

        # Portfolio frame
        self.portfolio_label = tk.Label(root, text="Portfolio Value: $0", font=("Arial", 12, "bold"))
        self.portfolio_label.pack(pady=5)
        self.holdings_label = tk.Label(root, text="Holdings: None", font=("Arial", 10))
        self.holdings_label.pack(pady=5)

        # Table frame
        self.tree = ttk.Treeview(root, columns=("Symbol", "Price", "Status"), show='headings')
        self.tree.heading("Symbol", text="Symbol")
        self.tree.heading("Price", text="Price ($)")
        self.tree.heading("Status", text="Status")
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Refresh Button
        self.refresh_button = ttk.Button(root, text="Refresh Data", command=self.update_data)
        self.refresh_button.pack(pady=10)

        # Start automatic updates
        self.update_data()
        self.auto_update()

    def update_data(self):
        """Updates the table and portfolio data."""
        # Update stock data
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = fetch_live_data()
        for entry in data:
            self.tree.insert("", "end", values=(entry["symbol"], entry["price"], entry["status"]))

        # Update portfolio data
        portfolio_value, holdings = fetch_portfolio()
        if portfolio_value is not None:
            self.portfolio_label.config(text=f"Portfolio Value: ${portfolio_value:.2f}")
            holdings_text = " | ".join([f"{symbol}: {qty}" for symbol, qty in holdings.items()])
            self.holdings_label.config(text=f"Holdings: {holdings_text}" if holdings else "Holdings: None")

    def auto_update(self):
        """Automatically refreshes the data every 30 seconds."""
        self.update_data()
        self.root.after(30000, self.auto_update)  # Refresh every 30 seconds

# ✅ Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
