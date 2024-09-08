from pydantic import BaseModel
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os
from dotenv import load_dotenv
import json

load_dotenv()

class Explanation(BaseModel):
    decision: str
    reasoning: str

class SentimentAnalysis:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.openAI_model = "gpt-4o-2024-08-06"

        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.classifier = pipeline("text-classification", model=self.finbert_model, tokenizer=self.tokenizer)

    def gpt_title_relevance(self, title, ticker):   
        completion = self.client.beta.chat.completions.parse(
            model = self.openAI_model,
            messages = [
                {"role": "system",
                 "content": 'You are a financial analyst. Given an article title and a stock ticker, decide if the title of the article is relevant to the given stock. Your response should be either "Relevant" or "Discard" based on how much impact this article could have on the ticker/stock. Additionally, explain the reasoning behind your response in a concise manner.'
                },
                {"role": "user",
                 "content": f"Article Title: '{title}', Stock Ticker: '{ticker}'"
                }
            ],
            temperature= 0.5,
            max_tokens = 150,
            response_format = Explanation,
        )
        
        title_relevance = completion.choices[0].message.parsed        
        # Manually extract 'decision' and 'reasoning' from the output
        decision = title_relevance.decision
        reasoning = title_relevance.reasoning
    
        # Return a dictionary
        return {
            "decision": decision,
            "reasoning": reasoning
        }

    def gpt_article_sentiment(self, text, ticker):
        completion = self.client.beta.chat.completions.parse(
            model = self.openAI_model,
            messages = [
                {"role": "system",
                 "content": 'You are a financial analyst. You will be given the text of an article and a stock ticker. Analyze the sentiment of the articles text with respect to the given ticker. Your descion needs to be one of the following: "Positve", "Negative", or "Neutral" based off the overall sentiment of the article. Additionally, provide a concise explanation of your reasoning.'
                },
                {"role": "user",
                 "content": f"Article Text: '{text}', Stock Ticker: '{ticker}'"
                }
            ],
            temperature= 0.5,
            max_tokens = 200,
            response_format = Explanation
        )
        
        article_sentiment = completion.choices[0].message.parsed  # Already an Explanation object
        decision = article_sentiment.decision
        reasoning = article_sentiment.reasoning

        return {
            "decision": decision,
            "reasoning": reasoning
        }

    
    def finbert_article_sentiment(self, text):
        text = text[:512]
        results = self.classifier(text)
        sentiment_label = results[0]['label'].capitalize()  # Ensuring it matches "Positive", "Neutral", "Negative"
        return {"Sentiment": sentiment_label}