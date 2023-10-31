import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv('/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/src/config/.env')

class FinvizScraper:
    def __init__(self, driver_path, login_info):
        self.driver_path = driver_path
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.login_info = login_info  
        self.login()

    def login(self):
        print("attempting to login")
        self.driver.get("https://finviz.com/login.ashx")
        self.driver.find_element(By.NAME, "email").send_keys(self.login_info['FINVIZ_USERNAME'])
        self.driver.find_element(By.NAME, "password").send_keys(self.login_info['FINVIZ_PASSWORD'])
        self.driver.find_element(By.NAME, "remember").click()
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        print("logged in successfully")

    def select_preset(self, preset_name):
        self.driver.get("https://finviz.com/screener.ashx")
        # Assume preset buttons have a data attribute with the preset name
        preset_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"button[data-preset='{preset_name}']"))
        )
        preset_button.click()

    def scrape_and_update_tags(self):
        # Navigate to the table, scrape data, and update your tags accordingly
        pass

    def run(self):
        self.select_preset('PreJump')
        end_time = time.time() + (25 * 60)  # Run for 25 minutes
        while time.time() < end_time:
            self.scrape_and_update_tags()
            time.sleep(30)  # Wait for 30 seconds before the next scrape
    
    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    driver_path = os.getenv("DRIVER_PATH")
    login_info = {
        'FINFIZ_USERNAME': os.getenv('FINFIZ_USERNAME'),
        'FINFIZ_PASSWORD': os.getenv('FINFIZ_PASSWORD')
    }
    scraper = FinvizScraper(driver_path, login_info)
    scraper.run()
