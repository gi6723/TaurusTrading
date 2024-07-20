import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import justext
from newspaper import Article

def fetch_webpage_with_selenium(url):
    """
    Fetches the webpage content using Selenium for the given URL.
    
    Parameters:
        url (str): The URL of the webpage to fetch.
    
    Returns:
        str: The HTML content of the webpage.
    """
    # Set up the WebDriver
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load completely
        
        # Example of clicking a button to load more content, if necessary
        try:
            continue_button = driver.find_element(By.XPATH, '//*[@id="continue-reading-button-id"]')
            if continue_button:
                continue_button.click()
                time.sleep(2)  # Wait for the new content to load
        except Exception as e:
            print(f"No 'continue reading' button found: {e}")

        html_content = driver.page_source
        return html_content
    except Exception as e:
        print(f"Failed to fetch webpage using Selenium: {e}")
        return None
    finally:
        driver.quit()

def extract_with_justext(html):
    """
    Extracts content from a webpage using justext.
    
    Parameters:
        html (str): The HTML content of the webpage.
    
    Returns:
        str: The extracted content.
    """
    if html:
        paragraphs = justext.justext(html, justext.get_stoplist("English"))
        content = "\n".join([paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate])
        return content if content.strip() else "No meaningful content extracted with justext"
    else:
        return "Failed to fetch HTML content for justext extraction"

def extract_with_newspaper3k(url):
    """
    Extracts content from a webpage using newspaper3k.
    
    Parameters:
        url (str): The URL of the webpage to extract content from.
    
    Returns:
        str: The extracted content.
    """
    article = Article(url)
    try:
        article.download()
        article.parse()
        return article.text if article.text.strip() else "No meaningful content extracted with newspaper3k"
    except Exception as e:
        print(f"Failed to extract content: {e}")
        return f"Failed to extract content with newspaper3k: {e}"

# Example usage
url = 'https://finance.yahoo.com/m/4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b/magnificent-seven-stocks%3A.html'
html_content = fetch_webpage_with_selenium(url)
justext_content = extract_with_justext(html_content)
newspaper3k_content = extract_with_newspaper3k(url)

if justext_content:
    print("Extracted Content from justext:")
    print(justext_content)
else:
    print("Failed to extract content using justext")

if newspaper3k_content:
    print("\nExtracted Content from newspaper3k:")
    print(newspaper3k_content)
else:
    print("Failed to extract content using newspaper3k")
