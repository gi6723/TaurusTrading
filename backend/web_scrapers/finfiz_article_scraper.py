import json
import os
import time
from datetime import datetime, timedelta
from multiprocessing import Pool
from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from bs4 import BeautifulSoup


load_dotenv()

class FinFizArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        #options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        #self.driver.get("https://finviz.com/login.ashx")
        

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

    def login(self):
        username = os.getenv("FINVIZ_USERNAME")
        password = os.getenv("FINVIZ_PASSWORD")

        self.add_input_for_login(by=By.NAME, value="email", text=username)
        self.add_input_for_login(by=By.NAME, value="password", text=password)
        self.uncheck_remember_me_for_login()
        self.submit_for_login()

    def grab_tickers(self): #working
        tickers = []
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as file:
            data = json.load(file)
            for item in data:
                tickers.append(item["Ticker"])
            return tickers
    
    def ticker_search(self, tickers):
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, ":r0:"))
        )
        search_box.clear()
        search_box.send_keys(tickers)
        search_box.submit()
    
    def is_article_recent(self, date_str):
        now = datetime.utcnow()
        try:
            article_date = datetime.strptime(date_str, '%b-%d-%y %I:%M%p')
        except ValueError:
                return False

        if now.weekday() == 0:  # Monday
            threshold = now - timedelta(hours=48)
        else:
            threshold = now - timedelta(hours=24)

        return article_date >= threshold

    def fetch_article_data(self, ticker):
        self.ticker_search(ticker)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'news-table'))
        )

        table_html = self.driver.find_element(By.ID, 'news-table').get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, 'html.parser')
        rows = soup.find_all('tr', {'class': 'cursor-pointer has-label'})

        article_data = []
        for row in rows:
            try:
                date_published = row.find('td', {'align': 'right'}).text.strip()
                title = row.find('a', {'class': 'tab-link-news'}).text.strip()
                article_url = row.find('a', {'class': 'tab-link-news'}).get('href')
                publisher = row.find('div', {'class': 'news-link-right'}).text.strip()

                if self.is_article_recent(date_published):
                    article_data.append((title, article_url, date_published, publisher))
            except Exception as e:
                print(f"Error processing article: {e}")

        print(f"Found {len(article_data)} relevant articles for {ticker}")
        return article_data

    def fetch_article_text(self, url):
        self.driver.get(url)
        article_body = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text[:512]  # Truncate text to the model's maximum sequence length

    def close(self):
        self.driver.quit()

    def process_ticker(self):
        tickers = self.grab_tickers()
        for ticker in tickers:
            print(f"Processing ticker: {ticker}")
            article_data = self.fetch_article_data(ticker)
            print(f"Article data for {ticker}: {article_data}")
        self.close()

if __name__ == "__main__":
    scraper = FinFizArticleScraper()
    scraper.process_ticker()




















    
    


