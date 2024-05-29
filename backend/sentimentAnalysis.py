from transformers import BertTokenizer, BertForSequenceClassification, AutoTokenizer
import asyncio


class YahooFinanceScraper:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
