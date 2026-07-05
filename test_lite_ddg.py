import requests
from bs4 import BeautifulSoup

def test_lite_ddg(query):
    print(f"\n--- Testing Lite DDG ---")
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": query}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
            print(f"Found {len(links)} links")
            # print(resp.text[:500])
            return True
    except Exception as e:
        print(f"ERROR: {e}")
    return False

query = 'site:linkedin.com "Data Analyst" London "hiring" "@gmail.com"'
test_lite_ddg(query)
