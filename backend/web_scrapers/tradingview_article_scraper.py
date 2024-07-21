# Fetches articles from TradingView
import json
import os
from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class TradingViewArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def filter_articles(self, articles, retries=3):
        return
    
    def fetch_articles(self, ticker):
        self.driver.get(f"https://www.tradingview.com/symbols/NASDAQ-{ticker}/news/")

    def close(self):
        self.driver.quit()

    def process_ticker(self, ticker):
        self.fetch_articles(ticker)
        #self.driver.quit()

if __name__ == "__main__":
    scraper = TradingViewArticleScraper()
    scraper.process_ticker("NVDA")
    