from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import time 
from transformers import BertTokenizer, BertForSequenceClassification, AutoTokenizer
import asyncio


class YahooFinanceScraper:
    def __init__(self):
        #initialize webdriver and sentiment analyzer

        options = FirefoxOptions()
        # options.add_argument("--headless")
        #self.service = FirefoxService(GeckoDriverManager().install())
        #self.driver = webdriver.Firefox(service=self.service, options=options)
        #self.driver.get("https://finance.yahoo.com/")

    def json_parser(self):
        #read and return data from json file
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as file:
            data = json.load(file)
        return data

    def ticker_search(self, ticker):
        #use selenium to search for latest articles on Yahoo finance for a given ticker
        pass

    async def fetch(self, url):
        #Define async function to fetch data from a given url using aiohttp
        pass

    async def sentiment_analysis(self, data):
        #Define async function to analyze sentiment of articles
        pass

    async def process_ticker(self, ticker):
        #Define async function to process a given ticker
        pass

    def close(self):
        self.driver.close()

class ScraperManager(self):
    def __init__(self):
        #initialize the scraper manager
        self.scraper = YahooFinanceScraper()

    async def execute_yahoo_finance_scraper(self):
        #Define async function to execute the Yahoo Finance scraper
        pass

    def run(self):
        #Run the scraper manager
        pass

if __name__ == "__main__":
    manager = ScraperManager()
    manager.run()



    
    


