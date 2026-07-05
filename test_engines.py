import requests
from bs4 import BeautifulSoup
import re
import time

def test_engine(name, url, headers):
    print(f"\n--- Testing {name} ---")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            # Check for common bot detection strings
            if "captcha" in resp.text.lower() or "verify you are a human" in resp.text.lower():
                print(f"FAILED: Bot detection triggered for {name}")
                return False
            
            # Try to find some links
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
            print(f"Found {len(links)} links")
            if len(links) > 5:
                # print(links[:3])
                return True
        else:
            print(f"FAILED: Status {resp.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    return False

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

query = 'site:linkedin.com "Data Analyst" London "hiring" "@gmail.com"'
# Bing
test_engine("Bing", f"https://www.bing.com/search?q={requests.utils.quote(query)}", headers)
time.sleep(2)
# Yahoo
test_engine("Yahoo", f"https://search.yahoo.com/search?p={requests.utils.quote(query)}", headers)
time.sleep(2)
# DuckDuckGo (HTML version)
test_engine("DuckDuckGo HTML", f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}", headers)
