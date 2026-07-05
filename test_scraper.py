import scraper_service

query = 'site:linkedin.com "Data Analyst" AND ("hiring" OR "looking for") "@gmail.com" London'
print(f"Testing query: {query}")
try:
    results = scraper_service.autonomous_scrape_query(query, 5)
    print(f"Found {len(results)} results:")
    for r in results:
        print(r)
except Exception as e:
    print(f"Error: {e}")
