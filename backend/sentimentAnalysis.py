import asyncio
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os
import torch

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

load_dotenv()

class YahooFinanceScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("https://finance.yahoo.com/")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)

    async def fetch_article_data(self, ticker):
        print(f"Fetching article data for ticker: {ticker}")
        try:
            self.driver.get("https://finance.yahoo.com/")
            search_box = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='ybar-sbq']"))
            )
            search_box.clear()
            search_box.send_keys(ticker)
            search_box.submit()
            print(f"Searching for ticker: {ticker}")

            new_tab = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/section/aside/section/nav/ul/li[2]/a"))
            )
            new_tab.click()
            print(f"Navigated to news tab for ticker: {ticker}")

            articles_section = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/section/section/article/section[2]/div[2]/div/div/ul"))
            )
            articles = articles_section.find_elements(By.CLASS_NAME, "stream-item.svelte-7rcxn")
            print(f"Found {len(articles)} articles for ticker: {ticker}")

            article_data = []
            for article in articles:
                try:
                    headline_element = article.find_element(By.XPATH, ".//a[contains(@class, 'subtle-link')]")
                    headline = headline_element.get_attribute("title")
                    article_url = headline_element.get_attribute("href")
                    publisher_date_text = article.find_element(By.XPATH, ".//div[contains(@class, 'publishing font-condensed')]").text

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
                    print(f"Error processing article: {e}")
                except Exception as e:
                    print(f"Unexpected error processing article: {e}")

            print(f"Found {len(article_data)} relevant articles for {ticker}")
            return article_data
        except TimeoutException as e:
            print(f"TimeoutException for ticker {ticker}: {e}")
        except NoSuchElementException as e:
            print(f"NoSuchElementException for ticker {ticker}: {e}")
        except WebDriverException as e:
            print(f"WebDriverException for ticker {ticker}: {e}")
        except Exception as e:
            print(f"Unexpected error fetching articles for ticker {ticker}: {e}")
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

    async def analyze_sentiment(self, article_data):
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
        article_body = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text[:512]  # Truncate text to the model's maximum sequence length

    def sentiment_analysis(self, text):
        text = text[:512]  # Truncate text to the model's maximum sequence length
        results = self.nlp(text)
        sentiment_score = results[0]['score']
        sentiment_label = results[0]['label']
        print(f"Sentiment analysis result for '{text}': {results[0]}")
        return {"score": sentiment_score, "label": sentiment_label}

    async def process_ticker(self, ticker):
        article_data = await self.fetch_article_data(ticker)
        if not article_data:
            print(f"No relevant articles found for ticker: {ticker}")
            return []
        sentiment_scores = await self.analyze_sentiment(article_data)
        return sentiment_scores

    async def run_scraper(self, tickers):
        tasks = [self.process_ticker(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        return results

class SentimentAnalysisManager:
    def __init__(self):
        self.scraper = YahooFinanceScraper()

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

    async def run_analysis(self):
        tickers = self.read_tickers_from_json("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json")
        sentiment_data = await self.scraper.run_scraper(tickers)
        self.update_json_with_sentiment("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", sentiment_data)

if __name__ == "__main__":
    manager = SentimentAnalysisManager()
    asyncio.run(manager.run_analysis())
















    
    


