import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent.parent
output_dir = project_root / "assets" / "dataPrice"
output_dir.mkdir(parents=True, exist_ok=True)

class StockDataService:
    def __init__(self, symbol: str, period_months: int = 6):
        self.symbol = symbol
        self.period_months = period_months
        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=period_months * 30)

    def fetch_data(self):
        data = yf.download(self.symbol, start=self.start_date, end=self.end_date, auto_adjust=False)
        data.index = data.index.date

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        available_columns = [col for col in price_columns if col in data.columns]

        data['Date'] = data.index
        data = data[['Date'] + available_columns]

        for col in available_columns:
            data[col] = data[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

        return data

    def save_to_csv(self):
        data = self.fetch_data()
        file_path = output_dir / f"dataPrice{self.symbol}.csv"
        data.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")

if __name__ == "__main__":
    stock_service = StockDataService('TSLA')
    stock_service.save_to_csv()