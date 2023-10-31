import os
from dotenv import load_dotenv
from src.scraping.scraper import FinvizScraper
import time
# Load environment variables from .env file
load_dotenv('/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/src/config/.env')

driver_path = os.getenv('DRIVER_PATH')
login_info = {
    'FINVIZ_USERNAME': os.getenv('FINVIZ_USERNAME'),
    'FINVIZ_PASSWORD': os.getenv('FINVIZ_PASSWORD')
}

scraper = FinvizScraper(driver_path, login_info)

# Test login and initialization
scraper.login()

# Test preset selection
scraper.select_preset('PreJump')
time.sleep(60)
# ... and so on for the other methods
scraper.close()
