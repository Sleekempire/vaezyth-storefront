import requests
import time
import urllib.parse

target = "http://127.0.0.1:5050/api/trigger-scrape"

# Universal Sectors and Roles
sectors = [
    "Healthcare NHS", "Private Healthcare", "Retail UK", "E-commerce London",
    "Data Science Agency", "Tech Startup UK", "University Education", 
    "Primary School Education", "Digital Marketing Agency", "Financial Services",
    "Customer Support Center", "Logistics & Supply Chain"
]

roles = [
    "Business Analyst", "Data Analyst", "Customer Service Manager",
    "University Lecturer", "Teaching Assistant", "Digital Marketing Executive",
    "Operations Manager", "Sales Representative"
]

# Generate combinations
discovery_queries = []
for sector in sectors:
    for role in roles:
        query = f"{sector} '{role}' recruitment contact email London UK"
        discovery_queries.append(query)

print(f"Prepared {len(discovery_queries)} targeted search combinations.")

# Trigger in batches to not overwhelm the background worker
batch_size = 5
for i in range(0, len(discovery_queries), batch_size):
    batch = discovery_queries[i:i+batch_size]
    print(f"\n--- Batch {i//batch_size + 1} ---")
    for query in batch:
        data = {
            "query": query,
            "num_results": 50
        }
        print(f"Triggering: {query}...", end=" ", flush=True)
        try:
            # We use a 1s timeout for the trigger call itself so it doesn't hang
            response = requests.post(target, json=data, timeout=5)
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Triggered (Assumed backgrounding): {e}")
        
    print("Waiting 10 seconds for worker to stabilize...")
    time.sleep(10)

print("\nUniversal Discovery Phase Initialization Complete.")
