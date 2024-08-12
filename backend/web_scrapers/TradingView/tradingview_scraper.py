import json
import os
from datetime import datetime
import pytz
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import requests
import whisper
import certifi

# Load environment variables from the .env file
load_dotenv()

class TradingViewArticleScraper:
    def __init__(self, driver):
        self.driver = driver

    def grab_tickers(self):
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as f:
            data = json.load(f)
            tickers = [item["Ticker"] for item in data]
        f.close()
        return tickers

    def ticker_search(self, ticker):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "tv-header-search-container"))
            ).click()

            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "input-KLRTYDjH"))
            )
            search_box.clear()
            search_box.send_keys(ticker)
            search_box.send_keys(Keys.RETURN)

            self.switch_to_news_tab()

        except TimeoutException:
            print("Search box not found or not clickable")
        except NoSuchElementException:
            print("Search bar element could not be found")
        except Exception as e:
            print(f"An unexpected error occurred in ticker_search: {e}")

    def switch_to_news_tab(self):
        try:
            news_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'js-category-tab') and contains(@href, '/news/')]"))
            )
            news_tab.click()
    
        except TimeoutException:
            print("News tab is not clickable or could not be found")

    def extract_row_data(self, row):
        row_data = []
        website = "Trading View"
        article_title = row.find_element(By.CLASS_NAME, ".//a[contains(@class, 'title-HY0D0owe title-DmjQR0Aa')]").get_attribute("innerHTML").txt
        publisher = row.find_element(By.CLASS_NAME, "provider-HY0D0owe provider-TUPxzdRV").get_attribute("innerHTML").txt
        row_data.append({
        "Website": website,
        "Title": article_title,
        "Url": url,
        "Publisher": publisher,
        "Time": ""
        })

        print(row_data)
        return row_data

    def fetch_articles_and_text(self, tickers):
        for ticker in tickers:
            print(f"Searching for ticker: {ticker}")
            self.ticker_search(ticker)
            print(f"Finished searching for ticker: {ticker}, now looking for articles")
            try:
                container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list-iTt_Zp4a"))
                )
                print("Found article container")

                self.driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(2)

                for row in container.find_elements(By.XPATH, ".//a[contains(@class, 'card-HY0D0owe')]"):
                    try:
                        time_element = row.find_element(By.CLASS_NAME, "apply-common-tooltip")
                        time_title = time_element.get_attribute("title")

                        time_posted_naive = datetime.strptime(time_title, '%b %d, %Y, %H:%M %Z')
                        tz = pytz.timezone('US/Central') 
                        time_posted = tz.localize(time_posted_naive)

                        now = datetime.now(tz)
                        time_diff = now - time_posted
                        time_diff_minutes = time_diff.total_seconds() / 60
                        print(f"Time difference: {time_diff_minutes} minutes ago")

                        if time_diff_minutes < 24 * 60:
                            self.extract_row_data(row)

                        else:
                            break
                    except Exception as e:
                        print(f"Error: {e}")
            except Exception as e:
                print(f"Could not find container for {ticker}: {e}")





















