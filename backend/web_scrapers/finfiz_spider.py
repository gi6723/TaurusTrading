import json
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from readability import Document  # Ensure readability is correctly installed

load_dotenv()

class FinFizArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("https://finviz.com/login.ashx")
        self.filtered_data = []

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

    def article_data_filter(self, table_html):
        self.filtered_data = []
        soup = BeautifulSoup(table_html, 'html.parser')
        rows = soup.find_all('tr', {'class': 'cursor-pointer has-label'})
        TODAY = "Today"
        MONTHS = ["Jan-", "Feb-", "Mar-", "Apr-", "May-", "Jun-", "Jul-", "Aug-", "Sep-", "Oct-", "Nov-", "Dec-"]
        under_today = False

        for row in rows:
            if "sponsored" in row.get_text().lower():
                continue

            article_date = row.find('td', {'align': 'right'}).text.strip()

            if TODAY in article_date:
                time = article_date.replace(TODAY, '').strip()
                title = row.find('a', {'class': 'tab-link-news'}).text.strip()
                article_url = row.find('a', {'class': 'tab-link-news'}).get('href')
                publisher = row.find('div', {'class': 'news-link-right'}).text.strip()
                self.filtered_data.append((title, article_url, publisher, time))
                under_today = True
                
            elif under_today and not any(month in article_date for month in MONTHS):
                time = article_date
                title = row.find('a', {'class': 'tab-link-news'}).text.strip()
                article_url = row.find('a', {'class': 'tab-link-news'}).get('href')
                publisher = row.find('div', {'class': 'news-link-right'}).text.strip()
                self.filtered_data.append((title, article_url, publisher, time))
            else:
                under_today = False
        return self.filtered_data

    def fetch_article_table(self, ticker):
        self.ticker_search(ticker)

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'news-table'))
        )

        table_html = self.driver.find_element(By.ID, 'news-table').get_attribute('outerHTML')
        self.article_data_filter(table_html)
        
    def fetch_article_text(self, url):
        self.driver.get(url)
        article_body = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text[:512]  # Truncate text to the model's maximum sequence length

    def close(self):
        self.driver.quit()

    def process_ticker(self):
        self.login()
        tickers = self.grab_tickers()
        all_articles = []
        
        for ticker in tickers:
            print(f"Processing ticker: {ticker}")
            self.fetch_article_table(ticker)
            
            for article in self.filtered_data:
                title, article_url, publisher, time = article
                try:
                    article_text = self.fetch_article_text(article_url)
                except TimeoutException:
                    article_text = "Could not fetch article text."
                all_articles.append({
                    "Ticker": ticker,
                    "Title": title,
                    "URL": article_url,
                    "Publisher": publisher,
                    "Time": time,
                    "Text": article_text
                })
                
        self.close()
        
        # Convert to DataFrame
        articles_df = pd.DataFrame(all_articles)
        print(articles_df)
        return articles_df

if __name__ == "__main__":
    scraper = FinFizArticleScraper()
    articles_df = scraper.process_ticker()

















