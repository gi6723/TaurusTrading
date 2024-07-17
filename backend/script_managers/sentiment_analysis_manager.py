


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
        with Pool(processes=4) as pool:
            sentiment_data = pool.map(process_ticker, tickers)
        self.update_json_with_sentiment("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", sentiment_data)