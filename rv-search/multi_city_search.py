#!/usr/bin/env python3
"""
Multi-city Craigslist RV search with requests
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup

# Cities to search
CITIES = [
    'newyork', 'losangeles', 'sfbay', 'chicago', 'austin', 'boston', 'seattle',
    'atlanta', 'miami', 'portland', 'denver', 'dallas', 'houston', 'phoenix',
    'philadelphia', 'detroit', 'minneapolis', 'tampa', 'orlando', 'charlotte',
    'nashville', 'lasvegas', 'sandiego', 'sacramento', 'columbus', 'indianapolis',
    'cleveland', 'pittsburgh', 'stlouis', 'saltlakecity', 'albuquerque',
    'milwaukee', 'baltimore', 'jacksonville', 'memphis', 'neworleans',
    'louisville', 'raleigh', 'birmingham', 'tucson', 'fresno', 'omaha'
]

SEARCH_QUERIES = ['motorhome', 'class+c', 'camper+van']

results = {
    'cities_searched': [],
    'listings_found': [],
    'search_log': []
}

def search_city(city, query):
    """Search a city for RVs"""
    url = f"https://{city}.craigslist.org/search/rva?max_price=1500&query={query}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Simple count - look for "result" text
            count_match = re.search(r'(\d+)\s*-\s*\d+\s*of\s*(\d+)', response.text)
            if count_match:
                total = int(count_match.group(2))
                return {
                    'city': city,
                    'query': query,
                    'url': url,
                    'total_results': total,
                    'status': 'success'
                }
            else:
                # Check for zero results
                if 'Zero local results' in response.text or 'No results' in response.text:
                    return {
                        'city': city,
                        'query': query,
                        'url': url,
                        'total_results': 0,
                        'status': 'zero_results'
                    }
        return {
            'city': city,
            'query': query,
            'url': url,
            'status': f'error_{response.status_code}'
        }
    except Exception as e:
        return {
            'city': city,
            'query': query,
            'url': url,
            'status': f'error: {str(e)}'
        }

print("Starting multi-city Craigslist search...")
print(f"Cities to search: {len(CITIES)}")
print(f"Queries per city: {len(SEARCH_QUERIES)}")
print(f"Total searches: {len(CITIES) * len(SEARCH_QUERIES)}")
print()

# Search first 10 cities as a sample
for city in CITIES[:10]:
    for query in SEARCH_QUERIES:
        result = search_city(city, query)
        results['search_log'].append(result)
        
        if result.get('total_results', 0) > 0:
            print(f"✓ {city}/{query}: {result['total_results']} results")
        else:
            print(f"✗ {city}/{query}: no results")
        
        time.sleep(1)  # Rate limiting

# Save results
with open('/workspace/rv-search/city_search_summary.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSearch complete. Results saved to city_search_summary.json")
print(f"Total cities searched: {len(set([r['city'] for r in results['search_log']]))}")
print(f"Cities with results: {len([r for r in results['search_log'] if r.get('total_results', 0) > 0])}")
