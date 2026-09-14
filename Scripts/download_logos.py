import os
import shutil
import pandas as pd
import requests
import urllib3
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REPO_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = REPO_ROOT / 'Data' / 'logos.snappy.parquet'
FAVICON_DIR = REPO_ROOT / 'favicons'
SCRAPED_DIR = REPO_ROOT / 'scraped_logos'
FINAL_DIR = REPO_ROOT / 'logos_final'

domains_df = pd.read_parquet(PARQUET_PATH)
domains_df['url'] = 'https://' + domains_df['domain']
domains_df['favicon_url'] = domains_df['url'] + '/favicon.ico'

for directory in (FAVICON_DIR, SCRAPED_DIR, FINAL_DIR):
    directory.mkdir(exist_ok=True)

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0 Safari/537.36'
}


def fetch_image(url):
    """Return image bytes for url, retrying once without SSL verification."""
    for verify in (True, False):
        try:
            response = requests.get(url, headers=request_headers, timeout=10, verify=verify)
        except requests.exceptions.SSLError:
            continue
        except requests.exceptions.RequestException:
            return None
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return response.content
    return None


def fetch_page(url):
    for verify in (True, False):
        try:
            response = requests.get(url, headers=request_headers, timeout=10, verify=verify)
        except requests.exceptions.SSLError:
            continue
        except requests.exceptions.RequestException:
            return None
        if response.status_code == 200:
            return response.text
    return None


def save_image(content, path):
    try:
        Image.open(BytesIO(content)).convert('RGBA').save(path)
        return True
    except Exception:
        return False


def download_logo(row):
    """Try the favicon first, then fall back to scraping the homepage icon link.

    Returns (source, message) where source is 'favicon', 'scrape' or None.
    """
    domain = row['domain']

    content = fetch_image(row['favicon_url'])
    if content and save_image(content, FAVICON_DIR / f'{domain}.png'):
        return 'favicon', f'[FAVICON OK] {domain}'

    html = fetch_page(f'https://{domain}')
    if html is None:
        return None, f'[FAIL] {domain} - unreachable'

    soup = BeautifulSoup(html, 'html.parser')
    icon_link = soup.find('link', rel=lambda value: value and 'icon' in str(value).lower())
    if not (icon_link and icon_link.get('href')):
        return None, f'[FAIL] {domain} - no icon found'

    logo_url = urljoin(f'https://{domain}', icon_link['href'])
    content = fetch_image(logo_url)
    if content and save_image(content, SCRAPED_DIR / f'{domain}.png'):
        return 'scrape', f'[SCRAPED OK] {domain}'

    return None, f'[FAIL] {domain} - icon could not be downloaded'


success_favicon = 0
success_scrape = 0

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(download_logo, row) for _, row in domains_df.iterrows()]
    for future in as_completed(futures):
        source, message = future.result()
        if source == 'favicon':
            success_favicon += 1
        elif source == 'scrape':
            success_scrape += 1
        print(message)

print('\nDownload completed.')
print(f'Favicon successful downloads: {success_favicon}')
print(f'Scraping successful downloads: {success_scrape}')
print(f'Total websites processed: {len(domains_df)}')

for source_dir in (FAVICON_DIR, SCRAPED_DIR):
    for file in os.listdir(source_dir):
        shutil.copy(source_dir / file, FINAL_DIR / file)

print(f"\nAll images have been copied to '{FINAL_DIR.name}/'")
print(f"Total images in '{FINAL_DIR.name}': {len(os.listdir(FINAL_DIR))}")
