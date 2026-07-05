import requests
import time

target = "http://127.0.0.1:5050/api/trigger-scrape"

queries = [
    "Professor of Data Science PhD supervisor email -Finance -UK",
    "Machine Learning research group head contact -Finance -UK",
    "Artificial Intelligence PhD position funding -Finance -UK",
    "Deep Learning lab supervisor professor -Finance -UK",
    "Computer Vision research lead PhD vacancies -Finance -UK",
    "Natural Language Processing PhD studentship -Finance -UK",
    "Big Data analytics research supervisor -Finance -UK",
    "Statistical Learning professor research group -Finance -UK"
]

for query in queries:
    data = {
        "query": query,
        "num_results": 100
    }
    print(f"Triggering scrape for: {query}...", end=" ", flush=True)
    try:
        response = requests.post(target, json=data)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Failed: {e}")
    
    # Small delay between triggers to let the background tasks queue up
    time.sleep(2)

print("\nAll scrapes triggered. The system will now begin searching across all these sectors.")
