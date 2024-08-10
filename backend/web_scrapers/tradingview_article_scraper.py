import json
import os
from datetime import datetime
import pytz
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import requests
import whisper
import certifi

# Load environment variables from the .env file
load_dotenv()

class TradingViewArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.user_agent = UserAgent()
        os.environ['SSL_CERT_FILE'] = certifi.where()

    def grab_tickers(self):
        with open("/Users/gianniioannou/Documents/GitHub Files/TaurusTrading/backend/temp.json", "r") as f:
            data = json.load(f)
            tickers = [item["Ticker"] for item in data]
        f.close()
        return tickers

    def add_input_for_login(self, by: By, value: str, text: str):
        try:
            field = self.driver.find_element(by=by, value=value)
            field.send_keys(text)
        except NoSuchElementException:
            print(f"Element with {by}={value} not found")

    def submit_for_login(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "submitButton-LQwxK8Bm"))
            )
            button = self.driver.find_element(by=By.CLASS_NAME, value="submitButton-LQwxK8Bm")
            self.scroll_and_click(button)
        except TimeoutException:
            print("Login button not found")
            return
    
    def signin_by_email(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "emailButton-nKAw8Hvt"))
            )
            email_button = self.driver.find_element(by=By.CLASS_NAME, value="emailButton-nKAw8Hvt")
            self.scroll_and_click(email_button)
        except TimeoutException:
            print("Email button not found")
            return

    def transcribe(self, audio_url):
        try:
            # Download the audio file
            headers = {'User-Agent': self.user_agent.random}
            response = requests.get(audio_url, headers=headers)
            with open('.temp.wav', 'wb') as f:
                f.write(response.content)
            
            # Transcribe the audio file using the Whisper model
            model = whisper.load_model("base")
            result = model.transcribe('.temp.wav')
            
            print(f"Transcription: {result['text'].strip()}")  # Print the transcription
            return result['text'].strip()
        except Exception as e:
            print(f"An error occurred while transcribing the audio: {e}")
            return None

    def click_recaptcha_checkbox(self):
        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, ".//iframe[@title='reCAPTCHA']"))
            )
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            self.scroll_and_click(checkbox)
            print("Clicked reCAPTCHA checkbox")
        except TimeoutException:
            print("reCAPTCHA checkbox not found or could not be clicked")
        finally:
            self.driver.switch_to.default_content()

    def request_audio_version(self):
        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
            )  
            audio_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))
            )
            self.scroll_and_click(audio_button)
            print("Requested audio challenge")
        except TimeoutException:
            print("Audio challenge button not found or could not be clicked")
        finally:
            self.driver.switch_to.default_content()
    
    def solve_audio_challenge(self):
        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
            )
            while True:
                audio_url = self.driver.find_element(By.ID, "audio-source").get_attribute("src")
                transcription = self.transcribe(audio_url)

                if transcription:
                    audio_response_field = self.driver.find_element(By.ID, "audio-response")
                    audio_response_field.send_keys(transcription)
                    verify_button = self.driver.find_element(By.ID, "recaptcha-verify-button")
                    self.scroll_and_click(verify_button)
                    print("submitted transcription")

                    time.sleep(2)

                    try:
                        error_message = self.driver.find_element(By.CLASS_NAME, "rc-audiochallenge-error-message")
                        if error_message.is_displayed():
                            print("Error message detected: Multiple correct solutions required. Retrying...")
                            continue
                    except NoSuchElementException:
                        print("No error message detected, moving on")
                        break    

                else:
                    print("Failed to transcribe audio")
        except Exception as e:
            print(f"An error occurred while solving the audio challenge: {e}")
        finally:
            self.driver.switch_to.default_content()
            self.submit_for_login()

    def recaptcha_bypass(self):
        try:
            print("Attempting to solve Recaptcha")
            self.click_recaptcha_checkbox()

            # Wait a bit to see if the image challenge appears
            time.sleep(2)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'bframe')]"))
                )
                print("Image challenge detected, attempting to switch to audio challenge")
                self.request_audio_version()
                self.solve_audio_challenge()
            except TimeoutException:
                print("No image challenge detected, checkbox clicked successfully")
        except NoSuchElementException as e:
            print(f"Recaptcha not found or could not be clicked: {e}")
        except Exception as e:
            print(f"An error occurred while trying to interact with the Recaptcha: {e}")
        finally:
            self.driver.switch_to.default_content()

    def scroll_and_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        try:
            element.click()
        except ElementClickInterceptedException:
            print("Element click intercepted, trying again")
            time.sleep(2)
            element.click()

    def login(self):
        try:
            self.driver.get("https://www.tradingview.com/accounts/signin/")
            username = os.getenv("TRADINGVIEW_USERNAME")
            password = os.getenv("TRADINGVIEW_PASSWORD")

            self.signin_by_email()
            self.add_input_for_login(by=By.ID, value="id_username", text=username)
            self.add_input_for_login(by=By.ID, value="id_password", text=password)
            self.submit_for_login()
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "recaptchaContainer-LQwxK8Bm"))
                )
                self.recaptcha_bypass()
            except Exception as e:
                print(f"No Recaptcha appeared or error occurred: {e}")
        except Exception as e:
            print(f"An error occurred during login: {e}")
    
    def ticker_search(self, ticker):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "tv-header-search-container"))
            ).click()

            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "input-KLRTYDjH"))
            )
            search_box.clear()
            search_box.send_keys(ticker)
            search_box.send_keys(Keys.RETURN)

            self.switch_to_news_tab()

        except TimeoutException:
            print("Search box not found or not clickable")
        except NoSuchElementException:
            print("Search bar element could not be found")
        except Exception as e:
            print(f"An unexpected error occurred in ticker_search: {e}")

    def switch_to_news_tab(self):
        try:
            news_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'js-category-tab') and contains(@href, '/news/')]"))
            )
            news_tab.click()
    
        except TimeoutException:
            print("News tab is not clickable or could not be found")
       
    def fetch_articles_and_text(self, tickers):
        for ticker in tickers:
            print(f"Searching for ticker: {ticker}")
            self.ticker_search(ticker)
            print(f"Finished searching for ticker: {ticker}, now looking for articles")
            try:
                container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list-iTt_Zp4a"))
                )
                print("Found article container")

                self.driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(2)

                for row in container.find_elements(By.XPATH, ".//a[contains(@class, 'card-HY0D0owe')]"):
                    try:
                        time_element = row.find_element(By.CLASS_NAME, "apply-common-tooltip")
                        time_title = time_element.get_attribute("title")

                        time_posted_naive = datetime.strptime(time_title, '%b %d, %Y, %H:%M %Z')
                        tz = pytz.timezone('US/Central') 
                        time_posted = tz.localize(time_posted_naive)

                        now = datetime.now(tz)
                        time_diff = now - time_posted
                        time_diff_minutes = time_diff.total_seconds() / 60
                        print(f"Time difference: {time_diff_minutes} minutes ago")

                        if time_diff_minutes > 24 * 60:
                            break
                    except Exception as e:
                        print(f"Could not find time element in shadow DOM: {e}")
            except Exception as e:
                print(f"Could not find container for {ticker}: {e}")


        
    def close(self):
        self.driver.quit()

    def process_ticker(self):
        self.login()
        tickers = self.grab_tickers()
        self.fetch_articles_and_text(tickers)
        #self.driver.quit()

if __name__ == "__main__":
    scraper = TradingViewArticleScraper()
    scraper.process_ticker()

















