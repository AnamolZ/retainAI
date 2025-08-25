"""
Stock Data Service Module
Fetches historical stock prices from Yahoo Finance and saves them to CSV.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# Project Paths
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[3]
OUTPUT_DIR = PROJECT_ROOT / "assets" / "dataPrice"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class StockDataService:
    """
    Fetches historical stock data for a given symbol and saves it as CSV.

    Attributes:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        period_months (int): Number of months of historical data to fetch.
        start_date (datetime): Start date for data fetching.
        end_date (datetime): End date for data fetching.
    """

    def __init__(self, symbol: str, period_months: int = 6):
        self.symbol = symbol.upper()
        self.period_months = period_months
        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=period_months * 30)

    # Data Fetching
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetches historical stock price data from Yahoo Finance.

        Returns:
            pd.DataFrame: Processed stock data including 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'.
        """
        data = yf.download(self.symbol, start=self.start_date, end=self.end_date, auto_adjust=False)
        data.index = data.index.date

        # Flatten MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        available_columns = [col for col in price_columns if col in data.columns]

        # Ensure 'Date' column exists
        data['Date'] = data.index
        data = data[['Date'] + available_columns]

        # Format numeric columns to two decimals
        for col in available_columns:
            data[col] = data[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

        return data
    
    # Save Data
    def save_to_csv(self) -> None:
        """
        Saves the fetched stock data to CSV in the project assets directory.
        """
        data = self.fetch_data()
        file_path = OUTPUT_DIR / f"dataPrice{self.symbol}.csv"
        data.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")