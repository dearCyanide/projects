import requests
import time
import logging
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Helper functions
def extract_title(html):
    """Extract page title from HTML."""
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return "untitled_page"

def sanitize_filename(title, max_length=80):
    """Sanitize filename for Windows."""
    title = re.sub(r'[\\/:*?"<>|]', "", title)   # Remove illegal chars
    title = re.sub(r"\s+", "_", title)           # Replace spaces
    return title[:max_length].rstrip("_")        # Limit length

# Fetch function
def fetch_page(
    url,
    headers=None,
    retries=5,
    base_delay=1,
    timeout=10
):
    if headers is None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.5993.90 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    attempt = 0
    while attempt < retries:
        try:
            logging.info(f"Attempt {attempt + 1} to fetch {url}")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            logging.info("Webpage fetched successfully!")
            return response.text
        except requests.RequestException as e:
            attempt += 1
            delay = base_delay * (2 ** (attempt - 1))
            logging.warning(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("All retries failed.")
                raise

# Storage Directory
BASE_DIR = r"C:\Users\USER\Documents\Data Science"
OUTPUT_DIR = os.path.join(BASE_DIR, "scraped_pages")

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.info(f"Scraped pages will be saved in: {OUTPUT_DIR}")

# URL List
urls = [
    "https://en.wikipedia.org/wiki/Data_science",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Artificial_intelligence"
]

# Scraping and storage
for url in urls:
    html = fetch_page(url)

    raw_title = extract_title(html)
    safe_title = sanitize_filename(raw_title)

    filename = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    logging.info(f"Saved raw HTML to {filename}")

print("All pages fetched and stored successfully.")