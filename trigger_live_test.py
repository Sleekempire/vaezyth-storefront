import requests

target = "http://127.0.0.1:5050/api/trigger-scrape"
data = {
    "query": "Data Analyst London hiring email",
    "num_results": 100
}

print(f"Triggering LIVE scrape test at {target}...")
try:
    response = requests.post(target, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Request failed: {e}")
