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
from ..sentiment_analysis.sent_analysis import SentimentAnalysis
from ..data_handler import DataHandler #added backend.
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

load_dotenv()

class TradingViewArticleScraper:
    def __init__(self, driver):
        self.driver = driver
        self.sentiment_analyzer = TradingViewSentimentAnalysis()
        self.data_handler = DataHandler("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json")

    def grab_tickers(self):
        return self.data_handler.get_tickers()

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

    def extract_ticker_from_logo(self, row):
        ticker_images = row.find_elements(By.XPATH, ".//ul[contains(@class, 'stack-L2E26Swf')]/li/img")
        tickers = [img.get_attribute('src').split('/')[-1].split('.')[0].upper() for img in ticker_images]
        return tickers

    def extract_row_data(self, row, time_diff_minutes):
        try:
            website = "Trading View"
            article_title = row.find_element(By.XPATH, ".//div[contains(@class, 'apply-overflow-tooltip') and contains(@class, 'title-HY0D0owe')]").text
            publisher = row.find_element(By.XPATH, ".//span[contains(@class, 'provider-HY0D0owe')]").text
            url = row.get_attribute("href")
            tickers_mentioned = self.extract_ticker_from_logo(row)
            time_posted_str = f"{time_diff_minutes:.2f} minutes ago"
            
            row_data = {
                "Website": website,
                "Title": article_title,
                "Url": url,
                "Publisher": publisher,
                "Tickers Mentioned": tickers_mentioned,
                "Time": time_posted_str
            }

            # Print the extracted row data            
            return row_data

        except NoSuchElementException as e:
            print(f"Element not found during row data extraction: {e}")
            return None
        except Exception as e:
            print(f"Error extracting row data: {e}")
            return None

    def fetch_articles_and_text(self, tickers):
        for ticker in tickers:
            self.ticker_search(ticker)
            try:
                container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list-iTt_Zp4a"))
                )

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

                        if time_diff_minutes < 48 * 60:  # temporarily changed to 48 hours for testing
                            data = self.extract_row_data(row, time_diff_minutes)

                            if data:
                                title_sentiment = self.sentiment_analyzer.gpt_title_relevance(data["Title"], ticker)
                                
                                if "relevant" in title_sentiment["decision"].lower():
                                    article_text = self.fetch_text(data["Url"])
                                    gpt_sentiment = self.sentiment_analyzer.gpt_article_sentiment(article_text, ticker)
                                    finbert_sentiment = self.sentiment_analyzer.finbert_article_sentiment(article_text)

                                    # Append the additional sentiment analysis to the data before saving
                                    data["Title Sentiment"] = title_sentiment
                                    data["Article Sentiment"] = gpt_sentiment
                                    data["FinBERT Sentiment"] = finbert_sentiment
                                    data["Article Text"] = article_text

                                    self.data_handler.append_article_data(data, ticker)
                                else:
                                    print(f"No relevant title sentiment found for ticker {ticker}")

                        else:
                            print(f"Article too old: {time_diff_minutes} minutes ago")

                    except Exception as e:
                        print(f"Error processing row for ticker {ticker}: {e}")
            except Exception as e:
                print(f"Could not find container for {ticker}: {e}")

    def fetch_text(self, url):
        try:
            # Open a new tab and navigate to the URL
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "body-KX2tCBZq"))
            )
            
            paragraphs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'body-KX2tCBZq body-pIO_GYwT content-pIO_GYwT')]//p")
            
            article_text = " ".join([p.text for p in paragraphs])
            
            self.driver.close()
            
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return article_text
        
        except Exception as e:
            print(f"An error occurred while fetching article text: {e}")
            self.driver.close()  # Ensure the tab is closed if there's an error
            self.driver.switch_to.window(self.driver.window_handles[0])
            return ""


























