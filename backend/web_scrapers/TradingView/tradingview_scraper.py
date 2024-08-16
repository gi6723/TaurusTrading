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
from sent_analysis import TradingViewSentimentAnalysis
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

load_dotenv()

class TradingViewArticleScraper:
    def __init__(self, driver):
        self.driver = driver
        self.sentiment_analyzer = TradingViewSentimentAnalysis()

    def grab_tickers(self):
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as f:
            data = json.load(f)
            tickers = [item["Ticker"] for item in data]
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

    def extract_ticker_from_logo(self, row):
        ticker_images = row.find_elements(By.XPATH, ".//ul[contains(@class, 'stack-L2E26Swf')]/li/img")
        tickers = [img.get_attribute('src').split('/')[-1].split('.')[0].upper() for img in ticker_images]
        return tickers

    def extract_row_data(self, row, time):
        try:
            website = "Trading View"
            
            # Extract the article title
            article_title = row.find_element(By.XPATH, ".//div[contains(@class, 'apply-overflow-tooltip') and contains(@class, 'title-HY0D0owe')]").text
            
            # Extract the publisher
            publisher = row.find_element(By.XPATH, ".//span[contains(@class, 'provider-HY0D0owe')]").text
            
            # Extract the URL from the <a> tag
            url = row.get_attribute("href") #might need to modify this to add the base URL
            
            # Extract the tickers mentioned
            tickers_mentioned = self.extract_ticker_from_logo(row)
            
            # Extract time
            time_posted = time
            
            row_data = {
                "Website": website,
                "Title": article_title,
                "Url": url,
                "Publisher": publisher,
                "Tickers Mentioned": tickers_mentioned,
                "Time": time_posted
            }

            title_sentiment = self.sentiment_analyzer.gpt_title_relevance(row_data)
            row_data["Title Sentiment"] = title_sentiment

            self.append_to_json(row_data)

            print(row_data)
            return row_data

        except NoSuchElementException as e:
            print(f"Element not found during row data extraction: {e}")
            return None
        except Exception as e:
            print(f"Error extracting row data: {e}")
            return None

    def append_to_json(self, row_data):
        # Load the existing data from the JSON file
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as f:
            data = json.load(f)

        # Find the correct ticker and add the article data
        for ticker_data in data:
            if ticker_data["Ticker"] == row_data["Tickers Mentioned"][0]:  # Assuming the first ticker in the list
                if "Articles" not in ticker_data:
                    ticker_data["Articles"] = []
                if "TradingView" not in ticker_data["Articles"]:
                    ticker_data["Articles"].append({"TradingView": []})

                # Append the row data to the TradingView articles
                ticker_data["Articles"][0]["TradingView"].append(row_data)
                break

        # Save the updated data back to the JSON file
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "w") as f:
            json.dump(data, f, indent=4)

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
                            data = self.extract_row_data(row, time_posted)

                            if "relevant" in data["Title Sentiment"].lower():
                                article_text = self.fetch_text(data["Url"])
                                gpt_sentiment = self.sentiment_analyzer.gpt_article_sentiment(article_text)
                                finbert_sentiment = self.sentiment_analyzer.finbert_article_sentiment(article_text)
                                
                                # Append the additional sentiment analysis to the JSON
                                data["Article Text"] = article_text
                                data["GPT Text Sentiment"] = gpt_sentiment
                                data["FinBERT Text Sentiment"] = finbert_sentiment
                                self.append_to_json(data)

                        else:
                            break
                    except Exception as e:
                        print(f"Error: {e}")
            except Exception as e:
                print(f"Could not find container for {ticker}: {e}")
    
    def fetch_text(self, url):
        try:
            # Open a new tab and navigate to the URL
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            
            # Wait for the article content to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "body-KX2tCBZq"))
            )
            
            # Find all paragraph elements within the article content
            paragraphs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'body-KX2tCBZq body-pIO_GYwT content-pIO_GYwT')]//p")
            
            # Combine all the paragraph texts into one blob
            article_text = " ".join([p.text for p in paragraphs])
            
            # Close the new tab
            self.driver.close()
            
            # Switch back to the original tab
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return article_text
        
        except Exception as e:
            print(f"An error occurred while fetching article text: {e}")
            self.driver.close()  # Ensure the tab is closed if there's an error
            self.driver.switch_to.window(self.driver.window_handles[0])
            return ""
























