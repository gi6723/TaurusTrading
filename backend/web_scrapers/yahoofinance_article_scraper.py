import json
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class YahooFinanceArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def extract_publisher(self, footer_text):
        parts = [part.strip() for part in footer_text.split('•')]

        if len(parts) < 2:
            raise ValueError("Footer text format is not as expected")

        publisher = parts[0]
        return publisher

    def extract_time(self, footer_text):
        parts = [part.strip() for part in footer_text.split('•')]

        if len(parts) < 2:
            raise ValueError("Footer text format is not as expected")
        
        time = parts[1]
        return time

    def to_json(self, ticker, filtered_articles):
        # Read the existing JSON data
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as file:
            data = json.load(file)

        # Update the data
        for item in data:
            if item["Ticker"] == ticker:
                if "Articles" not in item:
                    item["Articles"] = []
                item["Articles"].extend(filtered_articles)
                break
        else:
            print(f"Ticker {ticker} not found in the JSON data")

        # Write the updated data back to the JSON file
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "w") as file:
            json.dump(data, file, indent=4)

    def filter_articles(self, articles):
        filtered_articles = []
        soup = BeautifulSoup(articles, 'html.parser')
        try:
            rows = soup.find_all('li', {'class': 'stream-item yf-7rcxn'})
            if not rows:
                print("No articles found with the specified class.")
            for row in rows:
                article_date = row.find('div', {'class': 'footer yf-1044anq'})
                if article_date:
                    try:
                        time = self.extract_time(article_date.text)
                        if "hours ago" in time:
                            website = "yahoo finance"
                            article_title = row.find('a').get('title')
                            url = row.find('a').get('href').replace("\n", "")
                            publisher = self.extract_publisher(article_date.text)
                            filtered_articles.append({
                                "Website": website,
                                "Title": article_title,
                                "Url": url,
                                "Publisher": publisher,
                                "Time": ""
                            })
                        else:
                            continue
                    except ValueError as ve:
                        print(f"ValueError: {ve}")
                else:
                    print("Article date not found.")
        except Exception as e:
            print(f"Error filtering articles: {e}")
        
        return filtered_articles

    def fetch_articles(self, ticker):
        self.driver.get(f"https://finance.yahoo.com/quote/{ticker}/news/")

        try:
            # Wait for the element to be present
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "news-stream"))
            )
        except TimeoutException:
            print("Element with class 'news-stream' not found")
            return []

        try:
            grid_html = self.driver.find_element(By.CLASS_NAME, "news-stream").get_attribute('outerHTML')
            filtered_articles = self.filter_articles(grid_html)
        except NoSuchElementException:
            print("Element with class 'news-stream' was not found on the page.")
            return []
        except Exception as e:
            print(f"Error fetching article grid: {e}")
            return []
        
        return filtered_articles

    def close(self):
        self.driver.quit()

    def process_ticker(self, ticker):
        filtered_articles = self.fetch_articles(ticker)
        if filtered_articles:
            self.to_json(ticker, filtered_articles)
        self.close()

if __name__ == "__main__":
    scraper = YahooFinanceArticleScraper()
    scraper.process_ticker("NVDA")




