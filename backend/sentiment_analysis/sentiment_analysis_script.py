def sentiment_analysis(self, text):
        text = text[:512]  # Truncate text to the model's maximum sequence length
        results = self.nlp(text)
        sentiment_score = results[0]['score']
        sentiment_label = results[0]['label']
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sentiment analysis result for '{text[:50]}...': {results[0]}")
        return {"score": sentiment_score, "label": sentiment_label}

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

#self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        #self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        #self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)