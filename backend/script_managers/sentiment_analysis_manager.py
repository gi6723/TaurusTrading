import json
from multiprocessing import Pool
from web_scrapers.finfiz_article_scraper import FinFizArticleScraper
from sentiment_analysis.sentiment_analysis_script import SentimentAnalyzer

class SentimentAnalysisManager:
    def __init__(self):
        self.analyzer = SentimentAnalyzer()

    def read_tickers_from_json(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            return [item["Ticker"] for item in data]

    def update_json_with_sentiment(self, file_path, sentiment_data):
        with open(file_path, "r") as file:
            data = json.load(file)

        for item, articles in zip(data, sentiment_data):
            item["Articles"] = articles

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def run_analysis(self):
        tickers = self.read_tickers_from_json("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json")
        with Pool(processes=4) as pool:
            sentiment_data = pool.map(self.process_ticker, tickers)
        self.update_json_with_sentiment("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", sentiment_data)

    def process_ticker(self, ticker):
        scraper = FinFizArticleScraper()
        article_data = scraper.process_ticker(ticker)
        sentiment_scores = self.analyzer.analyze_sentiment(article_data)
        return sentiment_scores

if __name__ == "__main__":
    manager = SentimentAnalysisManager()
    manager.run_analysis()

