from boilerpy3 import extractors

def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch webpage: {e}")
        return None

def extract_with_boilerpipe(url):
    extractor = extractors.ArticleExtractor()
    html = fetch_webpage(url)
    if html:
        return extractor.get_content(html)
    else:
        return None

# Example usage
url = 'https://www.insidermonkey.com/blog/the-best-strategy-for-financial-freedom-and-retiring-early-1324609/'
main_content = extract_with_boilerpipe(url)

if main_content:
    print("Extracted Content:")
    print(main_content)
else:
    print("Failed to extract content")








