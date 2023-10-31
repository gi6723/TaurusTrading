from selenium import webdriver
import os
import requests
from dotenv import load_dotenv


driver = webdriver.Chrome()
load_dotenv("/Users/gianniioannou/Documents/GitHub Files/Real-time-Stock-Trend-Prediction-Engine/ApiKey.env")
api_key = os.getenv('TWELVE_DATA_API_KEY')

