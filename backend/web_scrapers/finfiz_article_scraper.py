import json
import os
from datetime import datetime
from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

load_dotenv()

class FinFizArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("https://finviz.com/login.ashx")
        
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

    def grab_tickers(self):
        tickers = []
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as file:
            data = json.load(file)
            for item in data:
                tickers.append(item["Ticker"])
            return tickers

    def ticker_search(self, ticker):
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id=":r0:"]'))  # Correct ID for the search box
        )
        search_box.clear()
        search_box.send_keys(ticker)
        search_box.send_keys(Keys.RETURN)  # Simulate pressing Enter key
        print(f"Searching for ticker: {ticker}")

    def fetch_article_text(self, url):
        self.driver.get(url)
        article_body = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text  # Fetch all article text

    def fetch_article_data(self, ticker):
        self.ticker_search(ticker)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'news-table'))
        )

        table_html = self.driver.find_element(By.ID, 'news-table').get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, 'html.parser')
        rows = soup.find_all('tr', {'class': 'cursor-pointer has-label'})

        article_data = []
        unique_titles = set()

        for row in rows:
            try:
                # Skip advertisements
                if "sponsored" in row.get_text().lower():
                    continue

                date_published = row.find('td', {'align': 'right'}).text.strip()
                title = row.find('a', {'class': 'tab-link-news'}).text.strip()
                article_url = row.find('a', {'class': 'tab-link-news'}).get('href')
                publisher = row.find('div', {'class': 'news-link-right'}).text.strip()

                # Only process articles from today
                if not date_published.startswith('Today'):
                    continue

                print(f"Found article - Title: {title}, Date: {date_published}, URL: {article_url}, Publisher: {publisher}")

                if title not in unique_titles:
                    unique_titles.add(title)
                    article_text = self.fetch_article_text(article_url)
                    article_data.append({
                        "title": title,
                        "url": article_url,
                        "date_published": date_published,
                        "publisher": publisher,
                        "article_text": article_text
                    })
            except Exception as e:
                print(f"Error processing article: {e}")

        print(f"Found {len(article_data)} relevant articles for {ticker}")
        return article_data

    def close(self):
        self.driver.quit()

    def process_ticker(self, ticker):
        self.login()
        article_data = self.fetch_article_data(ticker)
        print(f"Article data for {ticker}: {article_data}")
        self.close()
        return article_data

if __name__ == "__main__":
    scraper = FinFizArticleScraper()
    scraper.process_ticker()





