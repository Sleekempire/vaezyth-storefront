import requests
import time

target = "http://127.0.0.1:5050/api/trigger-scrape"

# Maximum Breadth Queries
broad_queries = [
    "Data Analyst hiring contact email USA -UK",
    "Business Analyst recruitment Toronto -UK",
    "Data Scientist visa sponsorship Switzerland -UK",
    "Data Engineer hiring contact email Berlin -UK",
    "BI Developer recruitment Singapore -UK",
    "Tableau Developer hiring contact email Dublin -UK",
    "Systems Analyst recruitment Melbourne -UK",
    "Reporting Analyst hiring contact email Dubai -UK",
    "Data Specialist recruitment Stockholm -UK",
    "Junior Business Analyst hiring contact email -UK",
    "Graduate Data Analyst recruitment -UK",
    "Operations Analyst hiring contact email -UK",
    "Insight Analyst recruitment Amsterdam -UK",
    "Quantitative Analyst hiring contact email Hong Kong -UK",
    "Research Analyst recruitment Johannesburg -UK"
]

print(f"Triggering {len(broad_queries)} broad-spectrum queries...")

for query in broad_queries:
    data = {
        "query": query,
        "num_results": 100
    }
    print(f"Triggering: {query}...", end=" ", flush=True)
    try:
        requests.post(target, json=data, timeout=5)
        print("Done.")
    except:
        print("Queued.")
    time.sleep(2)

print("\nBroad Discovery Triggered.")
