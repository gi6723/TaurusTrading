from selenium import webdriver 
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import json
import os

load_dotenv()

class preMarketDataCollection:
    def __init__(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        self.service = FirefoxService(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=self.service, options=options)
        self.driver.get("https://finviz.com/login.ashx")

    def login(self):
        username = os.getenv("FINVIZ_USERNAME")
        password = os.getenv("FINVIZ_PASSWORD")

        self.add_input_for_login(by=By.NAME, value="email", text=username)
        self.add_input_for_login(by=By.NAME, value="password", text=password)
        self.uncheck_remember_me_for_login()
        self.submit_for_login()

    def add_input_for_login(self, by: By, value: str, text: str):
        field = self.driver.find_element(by=by, value=value)
        field.send_keys(text)

    def submit_for_login(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "fv-button"))
        )
        button = self.driver.find_element(by=By.CLASS_NAME, value="fv-button")
        button.click()

    def uncheck_remember_me_for_login(self):
        checkbox = self.driver.find_element(by=By.NAME, value="remember")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)

        if checkbox.is_selected():
            try:
                checkbox.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", checkbox)

    def navigate_to_screener(self):
        screener_tab = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[3]/a"))
        )
        screener_tab.click()

        preset_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "screenerPresetsSelect"))
        )
        preset_object = Select(preset_element)
        preset_object.select_by_visible_text("s: PreJump")

    def grab_info_from_table(self):
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/thead'))
        )
        table_headers_html = self.driver.find_element(By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/thead').get_attribute('outerHTML')
        headers_soup = BeautifulSoup(table_headers_html, 'lxml')
        headers = [header.text.strip() for header in headers_soup.find_all('th')]

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/tbody'))
        )
        table_html_snapshot = self.driver.find_element(By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/tbody').get_attribute('outerHTML')

        body_soup = BeautifulSoup(table_html_snapshot, 'lxml')
        rows = []
        for row in body_soup.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                rows.append([cell.text.strip() for cell in cells])

        df = pd.DataFrame(rows, columns=headers)
        df.drop(columns='No.', inplace=True)
        df.drop(columns='PE', inplace=True)
        df.rename(columns={'\n\nVolume': 'Volume'}, inplace=True)
        df.reset_index(drop=True, inplace=True)  
        return df

    def close(self):
        self.driver.quit()

    def save_to_json(self, df, filename="/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json"):
        with open(filename, 'w') as f:
            f.write(df.to_json(orient='records', indent = 4))

    def get_data(self):
        self.login()
        self.navigate_to_screener()  
        df = self.grab_info_from_table()
        self.save_to_json(df)
        self.close()
        return df

if __name__ == "__main__":
    data_collector = preMarketDataCollection()
    data = data_collector.get_data()

