from enum import Enum
import time
import pandas as pd
import warnings
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent.parent
output_path = project_root / "assets" / "dataPrice" / "dataPrice"

class NepseScraper:
    class Page(Enum):
        TODAY_PRICE = "today-price"
        STOCK_TRADING = "stock-trading"

    def __init__(self):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox") # CRITICAL for running in Docker
        opts.add_argument("--disable-dev-shm-usage") # CRITICAL for running in Docker
        opts.add_argument("--disable-gpu")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        opts.add_argument("--log-level=3")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        self.driver.set_window_position(800, 0)
        self.driver.set_window_size(700, 900)

    def open_page(self, page=Page.TODAY_PRICE):
        self.driver.get(f"https://www.nepalstock.com/{page.value}")

    def close(self):
        time.sleep(3)
        self.driver.quit()

    def get_data_for_symbol(self, symbol, from_date, to_date):
        wait = WebDriverWait(self.driver, 10)

        from_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//label[text()='From']/following-sibling::input")))
        to_input = self.driver.find_element(By.XPATH, "//label[text()='To']/following-sibling::input")

        from_input.clear()
        to_input.clear()
        from_input.send_keys(from_date)
        to_input.send_keys(to_date)

        symbol_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Stock Symbol or Company Name']")
        symbol_input.clear()
        symbol_input.click()
        for ch in symbol:
            symbol_input.send_keys(ch)
        symbol_input.send_keys(Keys.ENTER)

        Select(self.driver.find_element(By.TAG_NAME, "select")).select_by_value("500")

        self.driver.find_element(By.XPATH,
            "//button[contains(@class, 'box__filter--search') and normalize-space(text())='Filter']"
        ).click()

        table = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table-responsive")))
        headers = [th.text.strip() for th in table.find_element(By.CLASS_NAME, "thead-light").find_elements(By.TAG_NAME, "th")]

        rows = table.find_elements(By.TAG_NAME, "tr")
        data = [[td.text for td in row.find_elements(By.TAG_NAME, "td")] for row in rows if row.find_elements(By.TAG_NAME, "td")]

        return pd.DataFrame(data, columns=headers)

def scrape_and_save(symbol):
    today = datetime.today()
    end_date_str = today.strftime("%m/%d/%Y")
    start_date_str = (today - timedelta(days=178)).strftime("%m/%d/%Y")

    scraper = NepseScraper()
    scraper.open_page(NepseScraper.Page.STOCK_TRADING)

    try:
        df_symbol = scraper.get_data_for_symbol(symbol, from_date=start_date_str, to_date=end_date_str)

        df_symbol['Total Traded Shares'] = df_symbol['Total Traded Shares'].str.replace(',', '', regex=False).astype(float)
        df_symbol['Close Price'] = df_symbol['Close Price'].astype(float)
        df_symbol['Max Price'] = df_symbol['Max Price'].astype(float)
        df_symbol['Min Price'] = df_symbol['Min Price'].astype(float)

        converted_df = pd.DataFrame({
            'Date': df_symbol['Date'],
            'Close': df_symbol['Close Price'],
            'High': df_symbol['Max Price'],
            'Low': df_symbol['Min Price'],
            'Volume': df_symbol['Total Traded Shares']
        })

        converted_df = converted_df.sort_values(by='Date')

        output_path.parent.mkdir(parents=True, exist_ok=True)
        converted_df.to_csv(output_path.with_name(f"dataPrice{symbol}.csv"), index=False)
    finally:
        scraper.close()

if __name__ == "__main__":
    scrape_and_save("NABIL")