import asyncio
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Rest of your code


load_dotenv()

class YahooFinanceScraper:
    def __init__(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("https://finance.yahoo.com/")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)
    
    def json_parser(self, detail):
        f = "/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json"
        with open(f, "r") as file:
            data = json.load(file)

            count = 0
            for item in data:
                if detail in item:
                    print(item[detail])
                    count += 1
                    if count >= 10:
                        break

    async def fetch_article_data(self, ticker):
        print(f"Fetching article data for ticker: {ticker}")
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='ybar-sbq']"))
        )
        search_box.clear()
        search_box.send_keys(ticker)
        search_box.submit()

        news_tab = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='News']"))
        )
        news_tab.click()

        articles = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='content svelte-w835pj']"))
        )
        
        article_data = []
        for article in articles:
            headline = article.find_element(By.XPATH, ".//a").get_attribute("title")
            article_url = article.find_element(By.XPATH, ".//a").get_attribute("href")
            publisher = article.find_element(By.XPATH, ".//div[@class='publishing font-condensed svelte-1k3af9g']").text
            date_published = article.find_element(By.XPATH, ".//div[@class='publishing font-condensed svelte-1k3af9g']").text.split("•")[1].strip()

            if self.is_article_recent(date_published):
                article_data.append((headline, article_url, date_published, publisher))

        print(f"Found {len(article_data)} relevant articles for {ticker}")
        return article_data

    def is_article_recent(self, date_str):
        now = datetime.utcnow()
        if "hour" in date_str:
            hours_ago = int(date_str.split()[0])
            article_date = now - timedelta(hours=hours_ago)
        elif "day" in date_str:
            days_ago = int(date_str.split()[0])
            article_date = now - timedelta(days=days_ago)
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
            headline_score = self.sentiment_analysis(headline)
            if headline_score > 0.5:  # Example threshold for relevance
                article_text = self.fetch_article_text(url)
                text_score = self.sentiment_analysis(article_text)
                sentiment_scores.append({
                    "headline": headline,
                    "headline_score": headline_score,
                    "article_text": article_text,
                    "text_score": text_score,
                    "date_published": date_published,
                    "publisher": publisher
                })
            else:
                print(f"Article '{headline}' is not relevant enough with score {headline_score}")

        return sentiment_scores

    def fetch_article_text(self, url):
        self.driver.get(url)
        article_body = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        return article_body.text

    def sentiment_analysis(self, text):
        results = self.nlp(text)
        sentiment_score = results[0]['score']
        print(f"Sentiment analysis result for '{text}': {results[0]}")
        return sentiment_score

    async def process_ticker(self, ticker):
        article_data = await self.fetch_article_data(ticker)
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







    
    


