from selenium import webdriver
from time import sleep
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone

driver = webdriver.Chrome()
load_dotenv("/Users/gianniioannou/Documents/GitHub Files/Real-time-Stock-Trend-Prediction-Engine/ApiKey.env")
api_key = os.getenv('TWELVE_DATA_API_KEY')

