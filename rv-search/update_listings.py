#!/usr/bin/env python3
import json

listings = [
    {
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
        "runs_drives_signals": ["runs good (title)", "454 engine", "good trans", "drove it here", "Onan generator", "sat 5 years"],
        "leak_signals": [],
        "is_motorized_likely": True,
        "no_leaks_claimed": False,
        "rv_type": "Class A",
        "odometer": 74000,
        "fuel": "gas",
        "engine": "8 cyl 454",
        "notes": "Sat for 5 years, needs brake master cylinder, batteries, fuel service. Suggests towing it. Has potential with good engine/trans. Not pretty but mechanically promising."
    },
    {
        "id": "reading_7957027121",
        "source": "craigslist",
        "title": "1972 Banner 20' motorhome for restoration - make offer",
        "price": 1000,
        "city": "Robesonia",
        "state": "PA",
        "region": "reading",
        "url": "https://reading.craigslist.org/rvs/d/robesonia-1972-banner-20-motorhome-for/7957027121.html",
        "image_path": None,
        "image_url": None,
        "description_snippet": "1972 Banner motorhome on a Dodge chassis. Restoration started 20 years ago - stopped due to owner's death. Sitting since he passed, all batteries dead. Some water damage at front drivers side. Rear passenger window shattered.",
        "runs_drives_signals": ["Dodge chassis", "automatic transmission"],
        "leak_signals": ["water damage at front drivers side"],
        "is_motorized_likely": True,
        "no_leaks_claimed": False,
        "rv_type": "Class C / Vintage Motorhome",
        "odometer": 96818,
        "fuel": "gas",
        "transmission": "automatic",
        "length_ft": 24,
        "title_status": "clean",
        "notes": "Restoration project stopped 20 years ago. Has water damage. All batteries dead. Been sitting long term. Needs full restoration."
    },
    {
        "id": "phoenix_1989jamboree",
        "source": "craigslist",
        "title": "1989 Jamboree motorhome not running",
        "price": 1200,
        "city": "Phoenix",
        "state": "AZ",
        "region": "phoenix",
        "url": "https://phoenix.craigslist.org/rvd/d/phoenix-1989-jamboree-motorhome-not/7963186442.html",
        "image_path": None,
        "image_url": None,
        "description_snippet": "Rodents chewed the wires on engine and battery cables. AC blows cold, electric and lights work, plumbing works. Has some minor leaks that have damaged the paneling but the roof is metal and seems solid. Floor is solid no soft spots. Good tires.",
        "runs_drives_signals": ["not running", "was running a year ago", "AC blows cold", "electric works", "lights work", "plumbing works", "good tires"],
        "leak_signals": ["minor leaks", "damaged the paneling", "needs sealing around vents"],
        "is_motorized_likely": True,
        "no_leaks_claimed": False,
        "rv_type": "Class C",
        "odometer": 95000,
        "fuel": "gas",
        "engine": "Ford V8 7.5L",
        "length_ft": 27,
        "title_status": "clean",
        "notes": "NOT currently running - rodent damage to wiring. Has minor leaks affecting interior. AC and electrical systems work. Solid floor. Needs wiring repair to run."
    }
]

with open('/workspace/rv-search/listings.json', 'w') as f:
    json.dump(listings, f, indent=2)

print(f"Updated listings.json with {len(listings)} motorized RVs")
print("\nSUMMARY:")
print(f"Total listings: {len(listings)}")
print(f"Price range: ${min(l['price'] for l in listings)} - ${max(l['price'] for l in listings)}")
print(f"Running/drivable: {len([l for l in listings if 'not running' not in str(l.get('runs_drives_signals', []))])} of {len(listings)}")
print(f"No leaks claimed: {len([l for l in listings if l.get('no_leaks_claimed')])} of {len(listings)}")
print(f"\nAll listings have leak issues or uncertain leak status.")

