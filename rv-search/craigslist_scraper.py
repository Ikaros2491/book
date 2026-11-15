#!/usr/bin/env python3
"""
Nationwide Craigslist RV Search
Searches for motorized RVs under $1500 across US cities
"""

import json
import re
import time
from datetime import datetime

# Initialize results
listings = []
search_log = []

# First listing: Southwind
listings.append({
    "id": "southjersey_7967128479",
    "source": "craigslist",
    "title": "Old Southwind... INSIDE OPICS COMING SOON, runs good...",
    "price": 500,
    "city": "Franklinville",
    "state": "NJ",
    "region": "south jersey",
    "url": "https://southjersey.craigslist.org/rvs/d/franklinville-old-southwind-inside/7967128479.html",
    "image_path": "/workspace/rv-search/images/southwind_7967128479.jpg",
    "image_url": "https://images.craigslist.org/00C0C_8vBJCYOJy7n_0CI0t2_600x450.jpg",
    "description_snippet": "We drove it here like 5 years ago... then it sat, I think it needs a brake master cylinder.. it's not nice, has a awesome 454 engine and good trans. Has an old Onan generator",
    "runs_drives_signals": ["runs good", "454 engine", "good trans", "drove it here", "Onan generator"],
    "leak_signals": [],
    "is_motorized_likely": True,
    "no_leaks_claimed": False,
    "rv_type": "Class A",
    "odometer": 74000,
    "notes": "Sat for 5 years, needs brake master cylinder, batteries, fuel service. Suggests towing it. Has potential with good engine/trans."
})

search_log.append({
    "city": "newyork",
    "url": "https://newyork.craigslist.org/search/rva?max_price=1500",
    "results_found": 38,
    "motorized_count": 2,
    "status": "searched"
})

# Save initial data
with open('/workspace/rv-search/listings.json', 'w') as f:
    json.dump(listings, f, indent=2)

print(f"Initialized with {len(listings)} listing(s)")
print(json.dumps(listings[0], indent=2))

