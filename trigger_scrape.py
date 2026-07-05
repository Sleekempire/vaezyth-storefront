import requests

target = "http://127.0.0.1:5050/api/trigger-scrape"
data = {
    "query": "Business Analyst hiring recruiting email @gmail.com OR @outlook.com OR @icloud.com",
    "num_results": 200
}

print(f"Triggering endpoint at {target} for 100 leads...")
response = requests.post(target, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
