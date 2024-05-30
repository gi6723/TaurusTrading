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
import time

load_dotenv()

class preMarketDataCollection:
    def __init__(self):
        options = FirefoxOptions()
        #options.add_argument("--headless")
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
        screener_tab = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[3]/a"))
        )
        screener_tab.click()

        preset_element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, "screenerPresetsSelect"))
        )
        preset_object = Select(preset_element)
        preset_object.select_by_visible_text("s: PreJump")

    def table_check(self):
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/thead'))
        )

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/tbody'))
        )

    def table_parsing(self):
        table_html_snapshot = self.driver.find_element(By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/tbody').get_attribute('outerHTML')

        body_soup = BeautifulSoup(table_html_snapshot, 'lxml')
        rows = []
        for row in body_soup.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                rows.append([cell.text.strip() for cell in cells])
        return rows

    def scrape_table_pages(self):
        #click change tab to order tickers based on greatest to least change
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/table/tbody/tr[4]/td/div/table/tbody/tr[5]/td/table/tbody/tr/td/table/thead/tr/th[10]'))
        ).click()

        self.table_check()
        all_rows = self.table_parsing()

        page_select = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, "pageSelect"))
        )
        select_object = Select(page_select)
        num_pages = len(select_object.options)

        for i in range(1, num_pages):
            print(f"Navigating to page {i+1}/{num_pages}")
            select_object.select_by_index(i)
            time.sleep(2)  # Wait for 2 seconds to ensure the page has fully loaded
            WebDriverWait(self.driver, 10).until(
                EC.staleness_of(select_object.options[i])
            )
            self.table_check()  # Ensure the next page is fully loaded
            rows = self.table_parsing()
            all_rows.extend(rows)

            # Refresh the Select object after each page change
            page_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "pageSelect"))
            )
            select_object = Select(page_select)

        #grabs table headers to be used as columns in df
        table_headers_html = self.driver.find_element(By.XPATH, '//*[@id="screener-table"]/td/table/tbody/tr/td/table/thead').get_attribute('outerHTML')
        headers_soup = BeautifulSoup(table_headers_html, 'lxml')
        headers = [header.text.strip() for header in headers_soup.find_all('th')]
        
        #Contructs and returns df of table and all of it's pages
        df = pd.DataFrame(all_rows, columns=headers)
        df.drop(columns='P/E', inplace=True)
        df.rename(columns={'\n\nVolume': 'Volume'}, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df['articleText'] = ""
        df['sentScore'] = "" 

        self.driver.quit()
        return df
        
    def save_to_json(self, df, filename="/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json"):
        with open(filename, 'w') as f:
            f.write(df.to_json(orient='records', indent = 4))

    def close(self):
        self.driver.quit()

    def get_data(self):
        self.login()
        self.navigate_to_screener()  
        df = self.scrape_table_pages()
        self.save_to_json(df)
        self.close()
        return df

if __name__ == "__main__":
    data_collector = preMarketDataCollection()
    data = data_collector.get_data()

#Add Check for multiple table pages to make sure all ticker are scraped due to 20 ticker display limit
#Click on Change tab above table to ensure that the ordering or tickers is from Greatest to least change
