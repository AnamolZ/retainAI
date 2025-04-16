import time
from datetime import timedelta, datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta

class NepseScraper:
    def __init__(self):
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--ignore-urlfetcher-cert-requests")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def start(self):
        url = f"https://www.nepalstock.com/today-price"  
        driver = self.driver
        driver.get(url)

    def stop(self):
        time.sleep(3)
        self.driver.quit()
    

    def fetch_data(self, date_MMDDYYYY):
        driver = self.driver

        wait = WebDriverWait(driver, 10)

        date_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[bsdatepicker]")))
        date_input.clear()
        date_input.send_keys(date_MMDDYYYY)

        """
        symbol_element = driver.find_element(By.XPATH, "//input[@placeholder='Stock Symbol or Company Name']");
        symbol_element.clear()
        symbol_element.send_keys(symbol, Keys.ENTER)
        """

        dropdown_entries = driver.find_element(By.TAG_NAME, "select")
        select = Select(dropdown_entries)
        select.select_by_value("500")

        filter_button = driver.find_element(By.XPATH, "//div[contains(@class, 'box__filter--wrap')]//button[contains(@class, 'box__filter--search') and text()='Filter']")
        filter_button.click()

        table = driver.find_element(By.CSS_SELECTOR, "table.table__lg")
        thead = table.find_element(By.CLASS_NAME, "thead-light")
        header_cells = thead.find_elements(By.TAG_NAME, "th")

        data = []
        header_texts = [cell.text.strip() for cell in header_cells]
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows :
            cols = row.find_elements(By.TAG_NAME, "td")
            if cols:
                data.append([col.text for col in cols])
        df = pd.DataFrame(data, columns=header_texts)
        return df

    def fetch_data_symbol(self, from_DDMMYYY, to_DDMMYYYY):
        pass
