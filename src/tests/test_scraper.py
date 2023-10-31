from src.scraping.scraper import FinvizScraper
from decouple import config

driver_path = config('DRIVER_PATH')  # Assuming DRIVER_PATH is the key in your .env file
login_info = {
    'FINVIZ_USERNAME': config('FINVIZ_USERNAME'),
    'FINVIZ_PASSWORD': config('FINVIZ_PASSWORD')
}

scraper = FinvizScraper(driver_path, login_info)

# Test login and initialization
scraper.login()

# Test preset selection
scraper.select_preset('PreJump')

# ... and so on for the other methods
