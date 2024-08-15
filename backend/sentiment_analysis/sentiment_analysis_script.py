from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# Performs sentiment analysis on articles text using FinBERT

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)

    def grab_artilce_data(self):
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as f:
            data = json.load(f)
        return data
        f.close()

    def sentiment_analysis(self, text):
        text = text[:512]  # Truncate text to the model's maximum sequence length
        results = self.nlp(text)
        sentiment_score = results[0]['score']
        sentiment_label = results[0]['label']
        print(f"Sentiment analysis result for '{text[:50]}...': {results[0]}")
        return {"score": sentiment_score, "label": sentiment_label}

    def analyze_sentiment(self, article_data):
        sentiment_scores = []
        for article in article_data:
            headline = article["title"]
            publisher = article["publisher"]
            
            headline_result = self.sentiment_analysis(headline)
            
            sentiment_scores.append({
                "headline": headline,
                "headline_score": headline_result["score"],
                "headline_label": headline_result["label"],
                "article_text": article_text,
                "publisher": publisher
            })
        return sentiment_scores

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    article_data = analyzer.grab_artilce_data()
    sentiment_scores = analyzer.analyze_sentiment(article_data)
    print(sentiment_scores)