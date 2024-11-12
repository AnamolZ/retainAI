import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockDataService:
    def __init__(self, symbol: str, period_months: int = 6):
        self.symbol = symbol
        self.period_months = period_months
        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=period_months * 30)
        self.monthly_data_path = 'MonthlyData.csv'

    def fetch_data(self):
        data = yf.download(self.symbol, start=self.start_date, end=self.end_date)
        data.index = data.index.date
        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        data[price_columns] = data[price_columns].apply(lambda x: x.map(lambda y: f"{y:.2f}"))
        headers = data.columns
        if isinstance(headers[0], tuple):
            headers_list = [col[0] for col in headers]
        else:
            headers_list = headers.tolist()
        data.columns = headers_list
        data['Date'] = data.index
        data = data[['Date'] + [col for col in data.columns if col != 'Date']]
        return data

    def save_to_csv(self, file_path: str):
        data = self.fetch_data()
        data.to_csv(file_path, index=False)

if __name__ == "__main__":
    stock_service = StockDataService('AMZN')
    stock_service.save_to_csv(r'..\dataPrice\dataPrice.csv')