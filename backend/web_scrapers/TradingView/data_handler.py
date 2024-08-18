import json

class DataHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_json(self):
        try:
            with open(self.file_path, "r") as f:
                content = f.read().strip()
                if not content:
                    # Handle empty file scenario
                    print("Warning: JSON file is empty.")
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []  # Return an empty list or handle accordingly
        except FileNotFoundError:
            print("Warning: JSON file not found.")
            return []

    def save_json(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_tickers(self):
        data = self.load_json()
        return [item["Ticker"] for item in data]

    def append_article_data(self, row_data, ticker):
        data = self.load_json()

        # Find the correct ticker and add the article data
        for ticker_data in data:
            if ticker_data["Ticker"].lower() == ticker.lower():  # Match with the passed-in ticker
                if "Articles" not in ticker_data:
                    ticker_data["Articles"] = []
                ticker_data["Articles"].append(row_data)
                break

        self.save_json(data)
