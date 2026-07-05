import requests
import time
import urllib.parse

target = "http://127.0.0.1:5050/api/trigger-scrape"

# Detailed Precision - Targeting Cities & Institutional Pages
locations = [
    "London", "Manchester", "Birmingham", "Leeds", "Bristol", 
    "Edinburgh", "Glasgow", "Cambridge", "Oxford", "Liverpool", 
    "Newcastle", "Sheffield", "Belfast", "Cardiff", "Nottingham"
]
sectors = [
    "NHS Trust HR", "University Recruitment Team", "Digital Strategy Agency", 
    "Venture Capital Portfolio", "FinTech Startup", "Retail Corporate Office",
    "Supply Chain Consultancy", "Data Science Laboratory"
]

roles = [
    "Business Analyst", "Technical Project Manager", 
    "Operations Lead", "Strategy Consultant"
]

print(f"[{time.strftime('%H:%M:%S')}] Initializing Precision Discovery across {len(locations)} cities...")

for city in locations:
    print(f"\n--- Sector Scan: {city} ---")
    for sector in sectors:
        for role in roles:
            # High-precision query structure: skip 'hiring' keywords to avoid job boards, 
            # target 'team' and 'people' pages.
            query = f"{city} {sector} {role} site:*.uk contact people email"
            data = {
                "query": query,
                "num_results": 40
            }
            try:
                # Fire and forget (backend backgrounds the task)
                requests.post(target, json=data, timeout=2)
                print(f"Requested: {city} {sector} {role}", flush=True)
            except: pass
            
            # Tiny delay to prevent API congestion
            time.sleep(0.5)

print(f"\n[{time.strftime('%H:%M:%S')}] Precision Scan active. Monitoring database for results.")
