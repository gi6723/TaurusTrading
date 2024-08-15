from openai import OpenAI
from transformers import pipeline
import os
from dotenv import load_dotenv


class TradingViewSentimentAnalysis:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.openAI_model = "chatgpt-4o-latest"
        self.finbert_model = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")  # Load the FinBERT model

    def get_title_relevance(self):
        openai.api_key = self.chatgpt_api_key
        
        # Create a prompt for GPT to determine the relevance of the title to the ticker
        prompt = f"Determine the relevance of the following title to a specific stock ticker: '{self.title}'. Is this article highly relevant, somewhat relevant, or not relevant at all? Explain your reasoning."
        
        response = openai.Completion.create(
            engine="text-davinci-003",  # or another engine
            prompt=prompt,
            max_tokens=100
        )
        
        relevance = response['choices'][0]['text'].strip()
        return relevance

    def article_text_sentiment(self):
        # Use FinBERT to analyze the sentiment of the article text
        sentiment_result = self.finbert_model(self.article_text)
        return sentiment_result

# Example of using the class
title = "Example Title About a Stock"
article_text = "The stock of XYZ Corporation is showing strong growth due to recent market trends."

sentiment_analyzer = TradingViewSentimentAnalysis(title, article_text)

title_relevance = sentiment_analyzer.get_title_relevance()
article_sentiment = sentiment_analyzer.article_text_sentiment()

print(f"Title Relevance: {title_relevance}")
print(f"Article Sentiment: {article_sentiment}")
