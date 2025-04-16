import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

class NepseScraper:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
#         options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--ignore-urlfetcher-cert-requests")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def fetch_data(self):
        url = f"https://merolagani.com/StockQuote.aspx"  
        self.driver.get(url)
        time.sleep(5)
        self.driver.quit()
#         df = pd.DataFrame(data)
#         df.sort_values("Date", inplace=True)
#         return df