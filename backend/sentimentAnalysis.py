from preMarketDataCollection import preMarketDataCollection
from transformers import pipeline
import asyncio
from pyppeteer import launch
import pandas as pd
from bs4 import BeautifulSoup
import torch
import atexit

class YahooFinanceScraper:
    def __init__(self):
        pass

    async def initialize(self):
        self.browser = await launch()
        self.page = await self.browser.newPage()

    async def scrape(self, ticker):
        await self.page.goto(f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch") #navigates to yahoo finance page 
        content = await self.page.content() # captures pages HTML
        page_soup = BeautifulSoup(content, 'lxml')

        article_list_items = page_soup.find_all('li', class_='js-stream-content') 

        valid_article_links = []
        for list_item in article_list_items:
            article_link = list_item.find('a', href=True)
            #time_stamp = list_item.find('span', text=lambda x: 'ago' in x)
            ad_label = list_item.find('a', text='Ad')

            if ad_label:
                continue
            else:
                link_url = f"https://finance.yahoo.com{article_link['href']}" if article_link['href'].startswith('/') else article_link['href']
                valid_article_links.append(link_url)
        print(valid_article_links)
    
    async def close(self):
        await self.browser.close()
        
class SentimentAnalyzer:
    def __init__(self):
        self.pipe = pipeline("text-classification", model="ProsusAI/finbert")

    async def analyze_sentiment(self, text):
        # Implement sentiment analysis logic here
        pass

class SentimentAnalysisManager:
    def __init__(self, df):
        self.df = df
        self.scraper = YahooFinanceScraper()
        self.analyzer = SentimentAnalyzer()

    async def run_analysis(self):
        await self.scraper.initialize()  # Initialize the scraper
        tasks = [self.analyze_ticker(ticker) for ticker in self.df['Ticker']]
        await asyncio.gather(*tasks)  # Run all tasks concurrently

    async def analyze_ticker(self, ticker):
        article_text = await self.scraper.scrape(ticker)
        sentiment = await self.analyzer.analyze_sentiment(article_text)
        # Process sentiment results here
        pass

async def main():
    print("Starting pre-market data collection...")
    df = preMarketDataCollection().get_data()
    print(df)
    manager = SentimentAnalysisManager(df)
    await manager.run_analysis()
    atexit.register(lambda: asyncio.run(manager.scraper.close()))
    #updated_df = manager.df

if __name__ == "__main__":
    asyncio.run(main())

