import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone

# Load environment variables from .env file
load_dotenv("/Users/gianniioannou/Documents/GitHub Files/Real-time-Stock-Trend-Prediction-Engine/ApiKey.env")

# Get the API key from the environment variable
api_key = os.getenv('TWELVE_DATA_API_KEY')

def get_stock_price(symbol):
    url = f'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': '1min',
        'apikey': api_key,
        'start_date': '2023-10-20',
        'end_date': '2023-10-21'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        central = timezone('US/Central')
        df['datetime'] = df['datetime'].dt.tz_localize('UTC').dt.tz_convert(central)
        market_open_time = central.localize(datetime.strptime('2023-10-20 09:30:00', '%Y-%m-%d %H:%M:%S'))
        market_30min_time = market_open_time + timedelta(minutes=30)
        df_filtered = df[(df['datetime'] >= market_open_time) & (df['datetime'] < market_30min_time)]
        return df_filtered
    else:
        print(f'Failed to retrieve data: {response.status_code}')
        return None

# Example usage:
symbol = 'AAPL'
stock_data = get_stock_price(symbol)

# Convert the price and volume columns to float
stock_data[['open', 'high', 'low', 'close', 'volume']] = stock_data[['open', 'high', 'low', 'close', 'volume']].astype(float)

# Display the DataFrame
print(stock_data)
