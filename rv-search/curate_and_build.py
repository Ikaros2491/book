#!/usr/bin/env python3
"""Curate clean RV candidates and build spreadsheet with photos."""

from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.request
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image as PILImage

ROOT = Path("/workspace/rv-search")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

TITLE_KEYS = [
    "old southwind",
    "champion dodge",
    "sports coach",
    "chevy motorhome",
    "runs a drives",
    "rv / great buy",
    "chieftain",
    "coachmen catalina",
    "winnebago brave",
    "banner 20",
    "fleetwood southwind",
    "bounder similar to breaking",
    "1978 winnebago",
    "jamboree motorhome",
]

JUNK = re.compile(
    r"(storage for your|we buy|consignment|transport by|roof repair|cover for|"
    r"cables|catalytic|stainless-steel)",
    re.I,
)
RUNS = re.compile(
    r"\b(runs?\s*(good|great|well|fine|strong|a\s*drives)?|"
    r"drives?\s*(good|great|well|fine|strong)?|running|drivable|driveable|"
    r"starts?\b|driven\s*(here|home|recently)|runs\s+and\s+drives|"
    r"ran\s+and\s+drove|ran\s+well)\b",
    re.I,
)
LEAK_BAD = re.compile(
    r"\b((roof\s*)?leaks?|leaking|water\s*damage|soft\s*spots?|mold|mildew|"
    r"need(?:s)?\s+to\s+have\s+the\s+roof\s+sealed)\b",
    re.I,
)
NO_LEAK = re.compile(
    r"\b(no\s*(roof\s*)?leaks?|leak[\s-]?free|no\s*water\s*damage|"
    r"inside\s*is\s*dry|dry\s*(inside|interior)|solid\s*(roof|floor)|"
    r"no\s*soft\s*spots?|tranny[-\s]*no\s*leaks)\b",
    re.I,
)
NOT_RUN = re.compile(
    r"\b(not\s*running|non[\s-]?running|doesn.?t\s*run|must\s*be\s*towed|for\s*parts)\b",
    re.I,
)

FB_CITIES = [
    ("nyc", "New York NY"),
    ("la", "Los Angeles CA"),
    ("sanfrancisco", "San Francisco CA"),
    ("chicago", "Chicago IL"),
    ("austin", "Austin TX"),
    ("boston", "Boston MA"),
    ("seattle", "Seattle WA"),
    ("atlanta", "Atlanta GA"),
    ("miami", "Miami FL"),
    ("portland", "Portland OR"),
    ("denver", "Denver CO"),
    ("dallas", "Dallas TX"),
    ("houston", "Houston TX"),
    ("phoenix", "Phoenix AZ"),
    ("philadelphia", "Philadelphia PA"),
    ("detroit", "Detroit MI"),
    ("minneapolis", "Minneapolis MN"),
    ("tampa", "Tampa FL"),
    ("orlando", "Orlando FL"),
    ("charlotte", "Charlotte NC"),
    ("nashville", "Nashville TN"),
    ("lasvegas", "Las Vegas NV"),
    ("sandiego", "San Diego CA"),
    ("sacramento", "Sacramento CA"),
    ("columbus", "Columbus OH"),
    ("indianapolis", "Indianapolis IN"),
    ("cleveland", "Cleveland OH"),
    ("pittsburgh", "Pittsburgh PA"),
    ("stlouis", "St Louis MO"),
    ("saltlakecity", "Salt Lake City UT"),
    ("albuquerque", "Albuquerque NM"),
    ("milwaukee", "Milwaukee WI"),
    ("baltimore", "Baltimore MD"),
    ("jacksonville", "Jacksonville FL"),
    ("memphis", "Memphis TN"),
    ("neworleans", "New Orleans LA"),
    ("louisville", "Louisville KY"),
    ("raleigh", "Raleigh NC"),
    ("birmingham", "Birmingham AL"),
    ("tucson", "Tucson AZ"),
    ("fresno", "Fresno CA"),
    ("omaha", "Omaha NE"),
]


def fetch(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.read().decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        print("fail", url, exc)
        return None


def parse(html_text: str) -> dict:
    out: dict = {"description": "", "image_url": None, "title": None, "price": None}
    m = re.search(r'<section id="postingbody">(.*?)</section>', html_text or "", re.S | re.I)
    if m:
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"^QR Code Link to This Post\s*", "", t)
        out["description"] = html.unescape(t)[:1200]
    imgs = re.findall(r"(https://images\.craigslist\.org/[^\"']+_600x450\.jpg)", html_text or "")
    if not imgs:
        imgs = re.findall(r"(https://images\.craigslist\.org/[^\"']+\.jpg)", html_text or "")
    if imgs:
        out["image_url"] = imgs[0]
    tm = re.search(r'<span id="titletextonly">([^<]+)</span>', html_text or "")
    if tm:
        out["title"] = html.unescape(tm.group(1).strip())
    pm = re.search(r'<span class="price">\$?([0-9,]+)</span>', html_text or "")
    if pm:
        out["price"] = int(pm.group(1).replace(",", ""))
    return out


def download_image(url: str, dest: Path) -> Path | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=30).read()
    except Exception as exc:  # noqa: BLE001
        print("img fail", exc)
        return None
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
        print("non-image", dest.name, data[:50])
        return None
    dest.write_bytes(data)
    return dest


def valid_image(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    head = p.read_bytes()[:3]
    if head == b"\xff\xd8\xff" or p.read_bytes()[:4] == b"\x89PNG":
        return str(p)
    return None


def thumb(path: str | None) -> Path | None:
    path = valid_image(path)
    if not path:
        return None
    src = Path(path)
    try:
        im = PILImage.open(src).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        print("thumb fail", src, exc)
        return None
    out = src.with_name(src.stem + "_thumb.jpg")
    im.thumbnail((220, 160))
    im.save(out, "JPEG", quality=85)
    return out


def score(title: str, desc: str) -> dict:
    text = f"{title}\n{desc}"
    runs = list(dict.fromkeys(m.group(0) for m in RUNS.finditer(text)))[:12]
    if NOT_RUN.search(text):
        runs = [r for r in runs if r.lower() not in ("running",)]
    leaks: list[str] = []
    for m in LEAK_BAD.finditer(text):
        start = max(0, m.start() - 8)
        chunk = text[start : m.end() + 1]
        if re.search(r"\bno\s+(roof\s+)?leaks?\b", chunk, re.I):
            continue
        if re.search(r"tranny[-\s]*no\s*leaks", text, re.I) and len(re.findall(r"leak", text, re.I)) <= 1:
            continue
        leaks.append(m.group(0))
    if re.search(r"minor\s+leaks?", text, re.I):
        leaks.append("minor leaks")
    leaks = list(dict.fromkeys(leaks))[:12]
    no_leaks = list(dict.fromkeys(m.group(0) for m in NO_LEAK.finditer(text)))[:12]
    not_running = bool(NOT_RUN.search(text))
    caveats = []
    for pat in [
        r"no\s*paper\s*work",
        r"no\s*title",
        r"without\s*brakes",
        r"no\s*brakes",
        r"gutted",
        r"PROJECT\s*CAMPER",
        r"project",
    ]:
        mm = re.search(pat, text, re.I)
        if mm:
            caveats.append(mm.group(0))
    appears = bool(runs) and not not_running
    if re.search(r"without\s*brakes|no\s*brakes", text, re.I):
        appears = False
    if appears and no_leaks and not leaks:
        tier = "best_match"
    elif appears and not leaks:
        tier = "running_no_leak_mention"
    elif appears:
        tier = "running_has_leak_risk"
    elif not_running:
        tier = "not_running_project"
    else:
        tier = "unclear_condition"
    return {
        "runs_drives_signals": runs,
        "leak_signals": leaks,
        "no_leak_signals": no_leaks,
        "no_leaks_claimed": bool(no_leaks) and not leaks,
        "appears_running": appears,
        "tier": tier,
        "caveats": list(dict.fromkeys(caveats)),
    }


def main() -> None:
    raw = json.loads((ROOT / "listings.json").read_text())
    cands = []
    seen = set()
    for item in raw:
        url = item.get("url") or ""
        title = item.get("title") or ""
        if not any(k in title.lower() for k in TITLE_KEYS):
            continue
        if JUNK.search(title):
            continue
        if url in seen:
            continue
        seen.add(url)
        cands.append(item)

    print("candidates", len(cands))
    final = []
    for item in cands:
        url = item["url"]
        print("enrich", item.get("price"), (item.get("title") or "")[:55])
        page = fetch(url)
        time.sleep(0.4)
        d = parse(page) if page else {}
        title = d.get("title") or html.unescape(item.get("title") or "")
        desc = d.get("description") or html.unescape(item.get("description_snippet") or "")
        price = d.get("price") if d.get("price") is not None else item.get("price")
        if price is None or price < 100 or price > 1500:
            print("  skip price", price)
            continue
        if JUNK.search(title) or JUNK.search(desc[:240]):
            print("  skip junk")
            continue
        image_url = d.get("image_url") or item.get("image_url")
        image_path = valid_image(item.get("image_path"))
        if image_url and not image_path:
            dest = ROOT / "images" / f"final_{re.sub(r'[^a-zA-Z0-9]+', '_', title)[:40]}_{price}.jpg"
            got = download_image(image_url, dest)
            if got:
                image_path = str(got)
        scored = score(title, desc)
        final.append(
            {
                "id": item.get("id"),
                "source": "craigslist",
                "title": title,
                "price": price,
                "city": item.get("city") or item.get("region"),
                "state": item.get("state") or "",
                "region": item.get("region") or "",
                "url": url,
                "image_path": image_path,
                "image_url": image_url,
                "description_snippet": desc[:1000],
                **scored,
                "notes": "",
            }
        )

    dedup = []
    keys = set()
    for row in final:
        key = (re.sub(r"\W+", "", row["title"].lower())[:40], row["price"])
        if key in keys:
            continue
        keys.add(key)
        dedup.append(row)

    order = {
        "best_match": 0,
        "running_no_leak_mention": 1,
        "running_has_leak_risk": 2,
        "unclear_condition": 3,
        "not_running_project": 4,
    }
    dedup.sort(key=lambda x: (order.get(x["tier"], 9), x["price"]))
    (ROOT / "listings_filtered.json").write_text(json.dumps(dedup, indent=2))
    print("FINAL", len(dedup))
    for row in dedup:
        print(f"${row['price']} [{row['tier']}] {row['title'][:60]} img={bool(row.get('image_path'))}")

    wb = Workbook()
    ws = wb.active
    ws.title = "RV Candidates"
    headers = [
        "Photo",
        "Tier",
        "Price",
        "Title",
        "Location",
        "Appears Running",
        "No Leaks Claimed",
        "Run/Drive Signals",
        "Leak Signals",
        "Caveats",
        "Listing URL",
        "Description",
        "Source",
    ]
    ws.append(headers)
    hf = PatternFill("solid", fgColor="1F4E79")
    hfont = Font(color="FFFFFF", bold=True)
    for c in range(1, len(headers) + 1):
        ws.cell(1, c).fill = hf
        ws.cell(1, c).font = hfont
    fills = {
        "best_match": PatternFill("solid", fgColor="C6EFCE"),
        "running_no_leak_mention": PatternFill("solid", fgColor="DDEBF7"),
        "running_has_leak_risk": PatternFill("solid", fgColor="FFF2CC"),
        "not_running_project": PatternFill("solid", fgColor="FCE4D6"),
        "unclear_condition": PatternFill("solid", fgColor="EDEDED"),
    }
    for i, w in enumerate([28, 24, 10, 44, 20, 14, 14, 28, 22, 22, 48, 55, 12], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30

    for idx, row in enumerate(dedup, start=2):
        ws.row_dimensions[idx].height = 125
        loc = ", ".join(x for x in [row.get("city"), row.get("state")] if x) or row.get("region", "")
        vals = [
            "",
            row["tier"],
            row["price"],
            row["title"],
            loc,
            "YES" if row["appears_running"] else "NO/UNCLEAR",
            "YES" if row["no_leaks_claimed"] else ("LEAK RISK" if row["leak_signals"] else "not stated"),
            "; ".join(row["runs_drives_signals"]),
            "; ".join(row["leak_signals"]),
            "; ".join(row.get("caveats") or []),
            row["url"],
            row["description_snippet"],
            row["source"],
        ]
        for col, val in enumerate(vals, 1):
            cell = ws.cell(idx, col, val)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if col == 2:
                cell.fill = fills.get(row["tier"], PatternFill())
            if col == 11 and val:
                cell.hyperlink = str(val)
                cell.font = Font(color="0563C1", underline="single")
        t = thumb(row.get("image_path"))
        if t:
            img = XLImage(str(t))
            img.anchor = f"A{idx}"
            ws.add_image(img)

    ws2 = wb.create_sheet("FB Marketplace Searches")
    ws2.append(["Metro", "Slug", "Query", "URL (open while logged into Facebook)"])
    for c in range(1, 5):
        ws2.cell(1, c).fill = hf
        ws2.cell(1, c).font = hfont
    r = 2
    for slug, label in FB_CITIES:
        for q in ["motorhome", "class c rv", "camper van", "winnebago"]:
            url = (
                f"https://www.facebook.com/marketplace/{slug}/search/"
                f"?query={q.replace(' ', '%20')}&maxPrice=1500&category=vehicles"
                f"&sortBy=creation_time_descend&radius=500"
            )
            ws2.cell(r, 1, label)
            ws2.cell(r, 2, slug)
            ws2.cell(r, 3, q)
            cell = ws2.cell(r, 4, url)
            cell.hyperlink = url
            cell.font = Font(color="0563C1", underline="single")
            r += 1
    for col, w in zip("ABCD", [22, 14, 14, 110]):
        ws2.column_dimensions[col].width = w

    ws3 = wb.create_sheet("Search Notes")
    for row in [
        ["Field", "Value"],
        ["Date", "2026-09-24"],
        ["Goal", "Running/drivable RV under $1500 with no leaks, USA-wide"],
        [
            "Facebook Marketplace",
            "Blocked by login wall in this environment. Use sheet 2 links while logged into Facebook.",
        ],
        [
            "Listings source",
            "Craigslist nationwide (~300 regions scraped for motorhome/class A-C/camper van/Winnebago under $1500)",
        ],
        ["best_match", "Seller claims running/drives AND no leaks"],
        ["running_no_leak_mention", "Claims running; leaks not mentioned (still verify)"],
        ["running_has_leak_risk", "Claims running but mentions leaks/water/roof seal needed"],
        ["not_running_project", "Not running / must tow"],
        [
            "Reality",
            "No pristine turn-key coaches found at this budget. Most are 1970s–90s projects. Verify title, roof, and drivability in person.",
        ],
    ]:
        ws3.append(row)
    ws3.column_dimensions["A"].width = 28
    ws3.column_dimensions["B"].width = 110

    out = ROOT / "USA_Drivable_RVs_Under_1500.xlsx"
    wb.save(out)

    with (ROOT / "USA_Drivable_RVs_Under_1500.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "tier",
            "price",
            "title",
            "city",
            "region",
            "appears_running",
            "no_leaks_claimed",
            "runs_drives_signals",
            "leak_signals",
            "caveats",
            "url",
            "image_url",
            "image_path",
            "description_snippet",
            "source",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in dedup:
            w.writerow(
                {
                    **{k: row.get(k) for k in fields if k not in ("runs_drives_signals", "leak_signals", "caveats")},
                    "runs_drives_signals": "; ".join(row.get("runs_drives_signals") or []),
                    "leak_signals": "; ".join(row.get("leak_signals") or []),
                    "caveats": "; ".join(row.get("caveats") or []),
                }
            )

    cards = []
    for row in dedup:
        img = row.get("image_path")
        try:
            img_src = str(Path(img).relative_to(ROOT)) if img else (row.get("image_url") or "")
        except Exception:
            img_src = row.get("image_url") or ""
        cards.append(
            f'<article class="card tier-{row["tier"]}">'
            f'<a href="{html.escape(row["url"])}" target="_blank" rel="noopener">'
            f'<img src="{html.escape(img_src)}" alt="" loading="lazy"/></a>'
            f'<div class="body"><div class="price">${row["price"]}</div>'
            f'<h2><a href="{html.escape(row["url"])}">{html.escape(row["title"])}</a></h2>'
            f'<div class="meta">{html.escape(str(row.get("city") or row.get("region") or ""))} · {row["tier"]}</div>'
            f'<p>{html.escape(row.get("description_snippet", "")[:280])}</p></div></article>'
        )
    (ROOT / "USA_Drivable_RVs_Under_1500.html").write_text(
        "<!DOCTYPE html><html><head><meta charset='utf-8'/>"
        "<title>USA Drivable RVs Under $1500</title>"
        "<style>body{font-family:Georgia,serif;background:#eef2f0;margin:0;padding:24px}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}"
        ".card{background:#fff;border:1px solid #ccd;overflow:hidden}"
        ".card img{width:100%;height:200px;object-fit:cover;background:#bbb;display:block}"
        ".body{padding:12px}.price{font-weight:bold;font-size:1.3rem}h2{font-size:1rem;margin:6px 0}"
        "h2 a{color:#123;text-decoration:none}.meta{color:#555;font-size:.85rem}"
        ".tier-best_match{outline:3px solid #2e7d32}"
        ".tier-running_no_leak_mention{outline:2px solid #1565c0}"
        ".tier-running_has_leak_risk{outline:2px solid #f9a825}"
        ".tier-not_running_project{outline:2px solid #ef6c00}"
        ".tier-unclear_condition{outline:2px solid #999}</style></head><body>"
        "<h1>USA drivable RVs under $1,500</h1>"
        "<p>Nationwide Craigslist results. Facebook Marketplace requires login here — "
        "see spreadsheet sheet 2 for FB search links. Green = running + no-leak claim.</p>"
        f'<div class="grid">{"".join(cards)}</div></body></html>'
    )
    print("Wrote", out)


if __name__ == "__main__":
    main()
