from preMarketDataCollection import preMarketDataCollection
from bs4 import BeautifulSoup
import pandas as pd
import asyncio
import pyppeteer
from aiohttp import ClientSession

class YahooFinanceScraper:
    def __init__(self):
        pass
        
    async def scrape(self, ticker):
        pass
    
    def analyze_sentiment(self, text):
        pass
class SentimentAnalysisManager:
    def __init__(self, tickers):
        self.tickers = tickers

    async def run_analysis(self):
        pass

    async def organize_results(self):
        pass
    
async def main():
    df = preMarketDataCollection().get_data()
    tickers = df['Ticker'].tolist()
    manager = SentimentAnalysisManager(tickers)
    sentiments = await manager.run_analysis()
    manager.organize_results(sentiments)


asyncio.run(main())
