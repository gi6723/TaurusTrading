import multiprocessing
import json
from web_scrapers.finfiz_article_scraper import FinFizArticleScraper
from web_scrapers.yahoofinance_article_scraper import YahooFinanceArticleScraper
'''
Run Using:

cd /Users/gianniioannou/Documents/GitHub\ Files/TaurusTrading/backend
python -m script_managers.article_scraper_manager
'''

def scrape_finviz(ticker):
    scraper = FinFizArticleScraper()
    scraper.process_ticker(ticker)
    scraper.close()

def scrape_yahoo_finance(ticker):
    scraper = YahooFinanceArticleScraper()
    scraper.process_ticker(ticker)
    scraper.close()

def load_tickers(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    tickers = [item["Ticker"] for item in data]
    return tickers

if __name__ == "__main__":
    json_file = "/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json"
    tickers = load_tickers(json_file)

    with multiprocessing.Pool(processes=4) as pool:
        # Scrape Finviz articles concurrently
        pool.map(scrape_finviz, tickers)
        # Scrape Yahoo Finance articles concurrently
        pool.map(scrape_yahoo_finance, tickers)




