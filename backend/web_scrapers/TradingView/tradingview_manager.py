from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from authentication import Authenticator
from tradingview_scraper import TradingViewArticleScraper

class TradingManager:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")  # Uncomment for headless mode
        self.driver = webdriver.Firefox(options=options)

        self.authenticator = Authenticator(self.driver)
        self.scraper = TradingViewArticleScraper(self.driver)

    def run(self):
        print("Starting login process...")
        self.authenticator.login()

        tickers = self.scraper.grab_tickers()
        print(f"Fetched tickers: {tickers}")

        print("Starting article scraping...")
        self.scraper.fetch_articles_and_text(tickers)

    def cleanup(self):
        print("Cleaning up and closing browser...")
        self.driver.quit()


if __name__ == "__main__":
    manager = TradingManager()
    manager.run()
    manager.cleanup()
    