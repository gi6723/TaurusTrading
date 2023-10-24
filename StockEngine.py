import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
from twelvedata import TDClient

load_dotenv("/Users/gianniioannou/Documents/GitHub Files/Real-time-Stock-Trend-Prediction-Engine/ApiKey.env")

api_key = os.getenv('TWELVE_DATA_API_KEY')

