import json
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

load_dotenv()

class FinFizArticleScraper:
    def __init__(self):
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.filtered_data = [
            ("Article 1", "https://www.insidermonkey.com/blog/the-best-strategy-for-financial-freedom-and-retiring-early-1324609/", "Publisher 1", "08:00AM"),
            ("Article 2", "https://investorplace.com/2024/07/the-6-5-million-bet-against-nvidia/", "Publisher 2", "09:00AM"),
            ("Article 3", "https://finance.yahoo.com/m/4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b/magnificent-seven-stocks%3A.html", "Publisher 3", "10:00AM")
        ]

    def fetch_article_text(self, url):
        try:
            print(f"Navigating to URL: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            print(f"Page loaded for URL: {url}")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            article_body = soup.find('article')
            if not article_body:
                article_body = soup.find('div', class_='entry-content') or soup.find('div', class_='content-without-wrap') or soup.find('div', class_='caas-body')
            if not article_body:
                article_body = soup.find('body')
            paragraphs = article_body.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            print(f"Fetched text for URL: {url}")
            return article_text[:512]  # Truncate text to 512 characters
        except TimeoutException:
            print(f"Timeout while fetching article text for URL: {url}")
            return "Could not fetch article text."
        except NoSuchWindowException:
            print(f"Error: Browser window was closed for URL: {url}")
            return "No window error"
        except WebDriverException as e:
            print(f"WebDriverException for URL: {url}: {e}")
            return "WebDriver error"
        except Exception as e:
            print(f"Unexpected error for URL: {url}: {e}")
            return "Unexpected error"

    def process_ticker(self):
        all_articles = []
        for article in self.filtered_data:
            title, article_url, publisher, time = article
            print(f"Fetching article: {title}")
            article_text = self.fetch_article_text(article_url)
            all_articles.append({
                "Title": title,
                "URL": article_url,
                "Publisher": publisher,
                "Time": time,
                "Text": article_text
            })
        self.close()
        
        # Convert to DataFrame
        articles_df = pd.DataFrame(all_articles)
        print(articles_df)
        return articles_df

    def close(self):
        print("Closing the browser.")
        self.driver.quit()

if __name__ == "__main__":
    scraper = FinFizArticleScraper()
    articles_df = scraper.process_ticker()




