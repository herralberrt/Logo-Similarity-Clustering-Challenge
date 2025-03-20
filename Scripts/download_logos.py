import pandas as pd
import requests
import urllib3
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
domains_df = pd.read_parquet('logos.snappy.parquet')
domains_df['url'] = 'https://' + domains_df['domain']
domains_df['favicon_url'] = domains_df['url'] + '/favicon.ico'
os.makedirs('favicons', exist_ok=True)
os.makedirs('scraped_logos', exist_ok=True)

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0 Safari/537.36'
}
success_favicon = 0
success_scrape = 0

def download_logo(row):
    global success_favicon, success_scrape
    domain = row['domain']
    try:
        response = requests.get(row['favicon_url'], headers=request_headers, timeout=10)
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            Image.open(BytesIO(response.content)).save(f'favicons/{domain}.png')
            success_favicon += 1
            return f"[FAVICON OK] {domain}"
    except requests.exceptions.ConnectionError as e:
        return f"[DNS FAIL] {domain} - {e}"
    except Exception:
        try:
            response = requests.get(row['favicon_url'], headers=request_headers, timeout=10, verify=False)
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                Image.open(BytesIO(response.content)).save(f'favicons/{domain}.png')
                success_favicon += 1
                return f"[FAVICON OK - NO SSL] {domain}"
        except requests.exceptions.ConnectionError as e:
            return f"[DNS FAIL] {domain} - {e}"
        except Exception:
            pass
          
    try:
        try:
            page = requests.get(f'https://{domain}', headers=request_headers, timeout=10)
        except requests.exceptions.ConnectionError as e:
            return f"[DNS FAIL] {domain} - {e}"
        except Exception:
            page = requests.get(f'https://{domain}', headers=request_headers, timeout=10, verify=False)

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if icon_link and icon_link.get('href'):
                logo_url = urljoin(f'https://{domain}', icon_link['href'])
                try:
                    img_response = requests.get(logo_url, headers=request_headers, timeout=10)
                    if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
                        Image.open(BytesIO(img_response.content)).save(f'scraped_logos/{domain}.png')
                        success_scrape += 1
                        return f"[SCRAPED OK] {domain}"
                except requests.exceptions.ConnectionError as e:
                    return f"[DNS FAIL] {domain} - {e}"
                except Exception:
                    try:
                        img_response = requests.get(logo_url, headers=request_headers, timeout=10, verify=False)
                        if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
                            Image.open(BytesIO(img_response.content)).save(f'scraped_logos/{domain}.png')
                            success_scrape += 1
                            return f"[SCRAPED OK - NO SSL] {domain}"
                    except requests.exceptions.ConnectionError as e:
                        return f"[DNS FAIL] {domain} - {e}"
        return f"[FAIL] {domain} - No icon found"
    except Exception as e:
        return f"[ERROR] {domain} - {e}"

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(download_logo, row) for _, row in domains_df.iterrows()]
    for future in as_completed(futures):
        print(future.result())

print("\nDownload completed.")
print(f"Favicon successful downloads: {success_favicon}")
print(f"Scraping successful downloads: {success_scrape}")
print(f"Total websites processed: {len(domains_df)}")r
os.makedirs('logos_final', exist_ok=True)

for file in os.listdir('favicons'):
    shutil.copy(os.path.join('favicons', file), os.path.join('logos_final', file))
for file in os.listdir('scraped_logos'):
    shutil.copy(os.path.join('scraped_logos', file), os.path.join('logos_final', file))

print("\nAll images have been copied to 'logos_final/'")
print(f"Total images in 'logos_final': {len(os.listdir('logos_final'))}")
print("\nProcess completed successfully.")
