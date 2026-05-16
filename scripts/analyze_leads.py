#!/usr/bin/env python3
"""
Every-2-day NINE client analysis.
Reads outreach/leads-*.md, fetches sitemaps for each business + their top
competitor, scores the gap, ranks by pricing opportunity, and writes
analysis/client-ranking-{date}.md with personalized first-email hooks.
"""

import datetime
import glob
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

KEY_PAGES = ["book", "booking", "schedule", "appointment", "reserv",
             "menu", "services", "pricing", "price", "contact",
             "about", "blog", "gallery", "team", "shop", "order"]

PRICING_TIERS = [
    (80,  "Full Rebuild",        "$8,000 – $18,000", "Complete redesign + booking + SEO foundation"),
    (50,  "Growth Package",      "$4,000 – $8,000",  "Redesign + 1 key integration (booking/ordering)"),
    (25,  "Upgrade Package",     "$2,000 – $4,000",  "Page additions + booking or SEO fix"),
    (10,  "Quick-Win Package",   "$800 – $2,000",    "Targeted fix: booking, speed, or local SEO"),
    (0,   "Maintenance/SEO",     "$300 – $800/mo",   "Ongoing SEO or content — site is close to good"),
]

NICHE_MARKET_FACTS = {
    "gym":        "Fitness app bookings grew 47% since 2023 — gyms without online scheduling lose ~30% of after-hours sign-ups.",
    "restaurant": "61% of diners check a restaurant's website before visiting. Google favours sites with online ordering in local pack rankings.",
    "salon":      "Salon clients who book online spend 28% more per visit on average. 40% of salon bookings now happen outside business hours.",
    "spa":        "Wellness searches on Google have grown 3× since 2020. Spas with booking widgets rank 2 positions higher on average.",
    "retail":     "Local retail sites with product pages indexed by Google see 4× more foot traffic from search than those without.",
    "default":    "Businesses with modern websites convert local search traffic at 3× the rate of those with outdated or missing sites.",
}


# ── HTTP helpers ────────────────────────────────────────────────────────────

def get(url: str, timeout: int = 8) -> str:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"    GET failed {url}: {e}", file=sys.stderr)
        return ""


def ddg_search(query: str) -> list[str]:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    html = get(url)
    urls = re.findall(r'class="result__a"[^>]*href="(https?://[^"&]+)"', html)
    # filter aggregators
    skip = {"yelp.com", "tripadvisor", "google.com", "facebook.com",
            "yellowpages", "bbb.org", "mapquest", "foursquare"}
    return [u for u in urls if not any(s in u for s in skip)]


# ── Sitemap parsing ─────────────────────────────────────────────────────────

def fetch_sitemap_urls(base_url: str) -> list[str]:
    """Try /sitemap.xml and /sitemap_index.xml; fall back to crawling /robots.txt."""
    base = base_url.rstrip("/")
    candidates = [
        f"{base}/sitemap.xml",
        f"{base}/sitemap_index.xml",
        f"{base}/wp-sitemap.xml",
    ]

    # also check robots.txt for Sitemap: directive
    robots = get(f"{base}/robots.txt")
    for line in robots.splitlines():
        if line.lower().startswith("sitemap:"):
            candidates.insert(0, line.split(":", 1)[1].strip())

    for url in candidates:
        xml = get(url)
        if not xml:
            continue
        try:
            root = ET.fromstring(xml)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]
            if locs:
                return locs
        except ET.ParseError:
            pass

    return []


def sitemap_profile(urls: list[str]) -> dict:
    slugs = [u.lower() for u in urls]
    found = {kp: any(kp in s for s in slugs) for kp in KEY_PAGES}
    return {
        "total": len(urls),
        "has_booking": any(found[k] for k in ["book", "booking", "schedule", "appointment", "reserv"]),
        "has_menu_or_services": any(found[k] for k in ["menu", "services", "pricing", "price", "shop", "order"]),
        "has_blog": found["blog"],
        "has_about": found["about"],
        "has_contact": found["contact"],
        "has_gallery": found["gallery"],
        "found_pages": [k for k, v in found.items() if v],
        "missing_pages": [k for k, v in found.items() if not v],
    }


# ── Competitor lookup ────────────────────────────────────────────────────────

def find_competitor(business_name: str, niche: str, city: str) -> str:
    query = f'best {niche} in "{city}" site reviews -"{business_name}"'
    results = ddg_search(query)
    return results[0] if results else ""


def detect_niche(name: str, url: str) -> str:
    text = (name + " " + url).lower()
    if any(w in text for w in ["gym", "fitness", "train", "crossfit", "yoga", "pilates"]):
        return "gym"
    if any(w in text for w in ["restaurant", "diner", "cafe", "bistro", "kitchen", "grill", "taqueria"]):
        return "restaurant"
    if any(w in text for w in ["nail", "hair", "salon", "beauty", "spa", "barber"]):
        return "salon"
    if any(w in text for w in ["spa", "wellness", "massage"]):
        return "spa"
    if any(w in text for w in ["shop", "store", "boutique", "retail"]):
        return "retail"
    return "default"


# ── Scoring ──────────────────────────────────────────────────────────────────

def opportunity_score(client: dict, competitor: dict) -> int:
    """0–100 score. Higher = bigger gap = higher-value project for NINE."""
    score = 0

    # page count gap vs competitor
    comp_total = competitor["total"] if competitor["total"] > 0 else 1
    page_ratio = client["total"] / comp_total
    if page_ratio < 0.2:
        score += 40
    elif page_ratio < 0.5:
        score += 25
    elif page_ratio < 0.8:
        score += 10

    # no website at all
    if client["total"] == 0:
        score += 40

    # missing key pages
    if not client["has_booking"]:
        score += 15
    if not client["has_menu_or_services"]:
        score += 10
    if not client["has_contact"]:
        score += 5
    if not client["has_blog"] and competitor["has_blog"]:
        score += 5
    if not client["has_gallery"] and competitor["has_gallery"]:
        score += 5

    return min(score, 100)


def pricing_tier(score: int) -> tuple:
    for threshold, name, price, desc in PRICING_TIERS:
        if score >= threshold:
            return name, price, desc
    return PRICING_TIERS[-1][1], PRICING_TIERS[-1][2], PRICING_TIERS[-1][3]


# ── Insight generator ────────────────────────────────────────────────────────

def generate_insight(lead: dict, client_profile: dict, comp_profile: dict, niche: str, score: int) -> str:
    name = lead["name"]
    city = lead.get("city", "your city")
    market_fact = NICHE_MARKET_FACTS.get(niche, NICHE_MARKET_FACTS["default"])

    lines = []

    if client_profile["total"] == 0:
        lines.append(f"**{name} has no website** — every Google search for {niche}s in {city} sends potential customers to competitors.")
    else:
        gap = comp_profile["total"] - client_profile["total"]
        if gap > 0:
            lines.append(
                f"**{name}'s site has {client_profile['total']} pages** vs your top competitor's {comp_profile['total']} — "
                f"that's {gap} fewer pages indexed by Google, meaning less search visibility."
            )

    if not client_profile["has_booking"] and comp_profile["has_booking"]:
        lines.append("Your competitor accepts bookings online — you don't, which means you're invisible to anyone searching after hours.")

    if not client_profile["has_menu_or_services"] and comp_profile["has_menu_or_services"]:
        lines.append("Your competitor lists services/pricing on their site. Customers who can't find pricing often move on.")

    lines.append(market_fact)

    tier_name, tier_price, tier_desc = pricing_tier(score)
    lines.append(f"**Recommended package:** {tier_name} ({tier_price}) — {tier_desc}.")

    return "\n> ".join(lines)


# ── Lead parsing ─────────────────────────────────────────────────────────────

def parse_leads_files() -> list[dict]:
    leads = []
    files = sorted(glob.glob("outreach/leads-*.md"), reverse=True)
    if not files:
        print("No leads files found in outreach/", file=sys.stderr)
        return []

    for filepath in files:
        city = ""
        city_match = re.search(r"leads-(.+?)-\d{4}-\d{2}-\d{2}\.md", filepath)
        city_slug = city_match.group(1) if city_match else "unknown"

        with open(filepath) as f:
            content = f.read()

        # extract city from heading
        heading = re.search(r"^# (.+?) Outreach Leads", content, re.M)
        city = heading.group(1) if heading else city_slug.replace("-", " ").title()

        # extract table rows: | name | url | phone | email | weakness |
        rows = re.findall(r"\|\s*(.+?)\s*\|\s*(https?://\S+|-)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", content)
        for name, url, phone, email, weakness in rows:
            if name.lower() in ("business", "---"):
                continue
            leads.append({
                "name": name.strip(),
                "url": url.strip() if url.strip() != "—" else "",
                "phone": phone.strip(),
                "email": email.strip(),
                "weakness": weakness.strip(),
                "city": city,
                "source_file": filepath,
            })

    return leads


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today()
    leads = parse_leads_files()
    if not leads:
        sys.exit(0)

    print(f"Analysing {len(leads)} leads...", file=sys.stderr)

    scored = []
    for lead in leads:
        name = lead["name"]
        url = lead["url"]
        city = lead["city"]
        niche = detect_niche(name, url)

        print(f"  [{niche}] {name}", file=sys.stderr)

        # client sitemap
        client_urls = fetch_sitemap_urls(url) if url else []
        client_profile = sitemap_profile(client_urls)
        time.sleep(0.8)

        # competitor sitemap
        comp_url = find_competitor(name, niche, city)
        comp_urls = fetch_sitemap_urls(comp_url) if comp_url else []
        comp_profile = sitemap_profile(comp_urls)
        time.sleep(0.8)

        score = opportunity_score(client_profile, comp_profile)
        tier_name, tier_price, tier_desc = pricing_tier(score)
        insight = generate_insight(lead, client_profile, comp_profile, niche, score)

        scored.append({
            "lead": lead,
            "niche": niche,
            "score": score,
            "tier_name": tier_name,
            "tier_price": tier_price,
            "client_pages": client_profile["total"],
            "comp_pages": comp_profile["total"],
            "comp_url": comp_url,
            "missing": client_profile["missing_pages"],
            "insight": insight,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    # build report
    lines = [
        f"# NINE Client Opportunity Ranking — {today.strftime('%B %d, %Y')}",
        "",
        f"**Leads analysed:** {len(scored)}  ",
        f"**Ranked by:** sitemap gap vs top competitor + missing key pages  ",
        "",
        "---",
        "",
    ]

    for rank, s in enumerate(scored, 1):
        lead = s["lead"]
        lines += [
            f"## {rank}. {lead['name']}",
            f"**City:** {lead['city']} | **Niche:** {s['niche'].title()} | **Opportunity Score:** {s['score']}/100  ",
            f"**Package:** {s['tier_name']} — {s['tier_price']}  ",
            f"**Contact:** {lead['phone']} | {lead['email']}  ",
            f"**Their site:** {lead['url'] or '_(none)_'} ({s['client_pages']} pages)  ",
            f"**Top competitor:** {s['comp_url'] or '_(not found)_'} ({s['comp_pages']} pages)  ",
            f"**Missing pages:** {', '.join(s['missing'][:6]) or 'none detected'}  ",
            "",
            "**First-email hook:**",
            f"> {s['insight']}",
            "",
            "---",
            "",
        ]

    # summary table at top
    summary = [
        "",
        "## Quick-Reference Table",
        "",
        "| Rank | Business | City | Score | Package | Price | Email |",
        "|---|---|---|---|---|---|---|",
    ]
    for rank, s in enumerate(scored, 1):
        lead = s["lead"]
        summary.append(
            f"| {rank} | {lead['name']} | {lead['city']} | {s['score']} | {s['tier_name']} | {s['tier_price']} | {lead['email']} |"
        )
    summary.append("")

    lines = lines[:6] + summary + lines[6:]

    os.makedirs("analysis", exist_ok=True)
    filename = f"analysis/client-ranking-{today.isoformat()}.md"
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"Saved: {filename}", file=sys.stderr)
    print(filename)


if __name__ == "__main__":
    main()
