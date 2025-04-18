import yfinance as yf
from services.webscrapper.nepseScrapper import *

class StockDataService:
    def __init__(self, period_months: int = 6, type: str = "YAHOO"):
        self.period_months = period_months
        self.end_date = datetime.today()
        self.start_date = self.end_date - timedelta(days=period_months * 30)
        self.monthly_data_path = 'MonthlyData.csv'
        self.type = type

    def fetch_data(self, symbol: str):
        if self.type == "YAHOO":
            data = yf.download(symbol, start=self.start_date, end=self.end_date)
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
        elif self.type == "NEPSE":
            scraper = NepseScraper()
            scraper.browse(NepseScraper.Page.STOCK_TRADING)
            data = scraper.fetch_data_symbol(symbol,
                                              from_MMDDYYY=self.start_date.strftime("%m/%d/%Y"),
                                              to_MMDDYYYY=self.end_date.strftime("%m/%d/%Y"))
            # yet to do manipulation (maybe not needed for now)
            return data
        else:
            print("ERROR : Didn't hear about this stock exchange in a while")

    def save_to_csv(self, file_path: str, symbol: str):
        data = self.fetch_data()
        data.to_csv(file_path, index=False)