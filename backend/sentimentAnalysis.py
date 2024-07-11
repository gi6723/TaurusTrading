import json
import os
import time
from datetime import datetime, timedelta
from multiprocessing import Pool
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from bs4 import BeautifulSoup
from dotenv import load_dotenv

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
load_dotenv()

class YahooFinanceScraper:
    def __init__(self):
        options = FirefoxOptions()
        #options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        #self.driver.get("https://finance.yahoo.com")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)

    def fetch_article_data(self, ticker):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Fetching article data for ticker: {ticker}")
        try:
            self.driver.get("https://finance.yahoo.com")
            search_box = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='ybar-sbq']"))
            )
            search_box.clear()
            search_box.send_keys(ticker)
            search_box.submit()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Searching for ticker: {ticker}")

            news_tab = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@data-test='NEWS']//a"))
            )
            news_tab.click()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Navigated to news tab for ticker: {ticker}")

            articles_section = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='Mb(10px) Ov(h) Pstart(25px) Pend(25px)']"))
            )
            articles = articles_section.find_elements(By.XPATH, ".//li[contains(@class, 'js-stream-content')]")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {len(articles)} articles for ticker: {ticker}")

            article_data = []
            for article in articles:
                try:
                    headline_element = article.find_element(By.XPATH, ".//a")
                    headline = headline_element.text
                    article_url = headline_element.get_attribute("href")
                    publisher_date_text = article.find_element(By.XPATH, ".//div[contains(@class, 'C(#959595)')]").text

                    if "•" in publisher_date_text:
                        publisher, date_published = publisher_date_text.split("•")
                        publisher = publisher.strip()
                        date_published = date_published.strip()
                    else:
                        publisher = publisher_date_text.strip()
                        date_published = ""

                    if self.is_article_recent(date_published):
                        article_data.append((headline, article_url, date_published, publisher))
                except NoSuchElementException as e:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error processing article: {e}")
                except Exception as e:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error processing article: {e}")

            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {len(article_data)} relevant articles for {ticker}")
            return article_data
        except TimeoutException as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] TimeoutException for ticker {ticker}: {e}")
        except NoSuchElementException as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] NoSuchElementException for ticker {ticker}: {e}")
        except WebDriverException as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] WebDriverException for ticker {ticker}: {e}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error fetching articles for ticker {ticker}: {e}")
        return []

    def is_article_recent(self, date_str):
        now = datetime.utcnow()
        if "hour" in date_str:
            hours_ago = int(date_str.split()[0])
            article_date = now - timedelta(hours=hours_ago)
        elif "day" in date_str:
            days_ago = int(date_str.split()[0])
            article_date = now - timedelta(days=days_ago)
        elif "yesterday" in date_str.lower():
            article_date = now - timedelta(days=1)
        else:
            return False

        if now.weekday() == 0:  # Monday
            threshold = now - timedelta(hours=48)
        else:
            threshold = now - timedelta(hours=24)

        return article_date >= threshold

    def analyze_sentiment(self, article_data):
        sentiment_scores = []
        for headline, url, date_published, publisher in article_data:
            headline_result = self.sentiment_analysis(headline)
            article_text = self.fetch_article_text(url)
            text_result = self.sentiment_analysis(article_text)
            sentiment_scores.append({
                "headline": headline,
                "headline_score": headline_result["score"],
                "headline_label": headline_result["label"],
                "article_text": article_text,
                "text_score": text_result["score"],
                "text_label": text_result["label"],
                "date_published": date_published,
                "publisher": publisher
            })
        return sentiment_scores

    def fetch_article_text(self, url):
        self.driver.get(url)
        article_body = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text[:512]  # Truncate text to the model's maximum sequence length

    def sentiment_analysis(self, text):
        text = text[:512]  # Truncate text to the model's maximum sequence length
        results = self.nlp(text)
        sentiment_score = results[0]['score']
        sentiment_label = results[0]['label']
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sentiment analysis result for '{text[:50]}...': {results[0]}")
        return {"score": sentiment_score, "label": sentiment_label}

    def close(self):
        self.driver.quit()

def process_ticker(ticker):
    scraper = YahooFinanceScraper()
    article_data = scraper.fetch_article_data(ticker)
    sentiment_scores = scraper.analyze_sentiment(article_data)
    scraper.close()
    return sentiment_scores

class SentimentAnalysisManager:
    def __init__(self):
        pass

    def read_tickers_from_json(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            return [item["Ticker"] for item in data]

    def update_json_with_sentiment(self, file_path, sentiment_data):
        with open(file_path, "r") as file:
            data = json.load(file)

        for item, sentiments in zip(data, sentiment_data):
            item["Sentiment Scores"] = sentiments

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def run_analysis(self):
        tickers = self.read_tickers_from_json("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json")
        with Pool(processes=4) as pool:  # Adjust the number of processes as needed
            sentiment_data = pool.map(process_ticker, tickers)
        self.update_json_with_sentiment("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", sentiment_data)

if __name__ == "__main__":
    manager = SentimentAnalysisManager()
    manager.run_analysis()




















    
    


