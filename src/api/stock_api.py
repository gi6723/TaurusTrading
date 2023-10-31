import os
from dotenv import load_dotenv

load_dotenv("/Users/gianniioannou/Documents/GitHub Files/Real-time-Stock-Trend-Prediction-Engine/ApiKey.env")
api_key = os.getenv('TWELVE_DATA_API_KEY')