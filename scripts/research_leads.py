#!/usr/bin/env python3
"""
Daily NINE lead researcher — no API keys required.
Primary: Overpass API (OpenStreetMap) — structured business data, real addresses/phones/websites.
Email enrichment: scrapes each business homepage for mailto links.
Fallback: DuckDuckGo HTML scraping when Overpass returns sparse results.
"""

import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

CITIES = [
    # US Tier 2 — lower competition, commercially ready budgets
    "Asheville, NC",
    "Boise, ID",
    "Chattanooga, TN",
    "Greenville, SC",
    "Savannah, GA",
    "Fort Collins, CO",
    "Eugene, OR",
    "Spokane, WA",
    "Knoxville, TN",
    "Huntsville, AL",
    "Madison, WI",
    "Ann Arbor, MI",
    "Burlington, VT",
    "Charlottesville, VA",
    "Flagstaff, AZ",
    "Santa Fe, NM",
    "Bend, OR",
    "Fayetteville, AR",
    "Lexington, KY",
    "Columbia, SC",
    "Wilmington, NC",
    "Richmond, VA",
    "Tulsa, OK",
    "Des Moines, IA",
    "Grand Rapids, MI",
    "Dayton, OH",
    "Springfield, MO",
    "Peoria, IL",
    "Wichita, KS",
    "Little Rock, AR",
    # UK Tier 2
    "Brighton, UK",
    "Bristol, UK",
    "Edinburgh, UK",
    "Cardiff, UK",
    "Norwich, UK",
    "Exeter, UK",
    "Bath, UK",
    "York, UK",
    "Oxford, UK",
    "Coventry, UK",
    # Australia Tier 2
    "Byron Bay, Australia",
    "Noosa, Australia",
    "Hobart, Australia",
    "Geelong, Australia",
    "Launceston, Australia",
    "Cairns, Australia",
    "Townsville, Australia",
    "Wollongong, Australia",
    "Gold Coast, Australia",
    "Sunshine Coast, Australia",
]

# (niche_key, osm_tag_pairs, ddg_fallback_query)
NICHES = [
    (
        "restaurants",
        [("amenity", "restaurant"), ("amenity", "cafe"), ("amenity", "bistro"), ("amenity", "bar")],
        "independent restaurant cafe bistro bar food",
    ),
    (
        "health_wellness",
        [("leisure", "fitness_centre"), ("amenity", "spa"), ("shop", "massage"), ("shop", "health_food"), ("amenity", "yoga")],
        "health wellness studio spa fitness supplement",
    ),
    (
        "fmcg",
        [("shop", "deli"), ("shop", "bakery"), ("shop", "health_food"), ("shop", "farm"), ("shop", "chocolate"), ("shop", "coffee")],
        "artisan food drink producer local brand packaged goods",
    ),
    (
        "events",
        [("amenity", "events_venue"), ("amenity", "community_centre"), ("tourism", "hotel"), ("leisure", "wedding_venue")],
        "event venue wedding venue event planner",
    ),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

PITCH = {
    "restaurants":     "Stunning food, flat socials — reels + a Google-optimised site turns browsers into bookings",
    "health_wellness": "Wellness is booming but their content doesn't show it — motion-heavy reels + influencer collab fills the gap",
    "fmcg":            "Great product, no visual identity online — brand spine + creator UGC puts product in front of buyers",
    "events":          "Event venues live and die by scroll-stopping visuals — no reel strategy = invisible to the couples/planners searching now",
}

EMAIL_TEMPLATE = """---

## Email Template

**Subject:** Quick question about [Business Name]'s content

Hi [Name],

I came across [Business Name] while looking at {niche} in {city} — love what you're doing.

One thing I noticed: [specific issue — flat socials / no reels / UGC missing].

We help businesses like yours turn that into scroll-stopping content — brand spine + 15 reels in 2 weeks, no long-term commitment.

Worth a quick chat this week?

[Your name]
NINE
"""


def pick_city(date: datetime.date) -> str:
    return CITIES[date.toordinal() % len(CITIES)]


# ── Overpass API (primary) ────────────────────────────────────────────────────

def overpass_search(city_name: str, tag_pairs: list, limit: int = 15) -> list:
    conditions = "\n  ".join(
        f'node["{k}"="{v}"](area.a);' for k, v in tag_pairs
    )
    query = f"""[out:json][timeout:30];
area["name"~"^{re.escape(city_name)}$",i]["admin_level"~"^(6|7|8|9|10)$"]->.a;
(
  {conditions}
);
out body {limit};"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=data,
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.loads(resp.read().decode()).get("elements", [])
    except Exception as e:
        print(f"  Overpass error: {e}", file=sys.stderr)
        return []


def parse_osm_element(el: dict) -> dict | None:
    tags = el.get("tags", {})
    name = tags.get("name", "").strip()
    if not name:
        return None
    website = (
        tags.get("website") or tags.get("url") or tags.get("contact:website") or ""
    ).strip().rstrip("/")
    phone = (
        tags.get("phone") or tags.get("contact:phone") or tags.get("mobile") or ""
    ).strip()
    email = (tags.get("email") or tags.get("contact:email") or "").strip()
    return {
        "name": name,
        "url": website or "—",
        "phone": phone or "—",
        "email": email or "—",
    }


# ── Email enrichment — scrape business homepage ───────────────────────────────

EMAIL_FALSE_POSITIVES = re.compile(
    r"(example\.|sentry\.|schema\.|wixpress\.|@2x|\.png|\.jpg|\.gif|noreply|no-reply)",
    re.I,
)


def scrape_email_from_site(url: str) -> str:
    if not url or url == "—":
        return "—"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")[:60000]
        # prefer mailto: links first — they're intentional
        mailto = re.search(r'href=["\']mailto:([\w.+\-]+@[\w.\-]+\.[a-z]{2,})', html, re.I)
        if mailto and not EMAIL_FALSE_POSITIVES.search(mailto.group(1)):
            return mailto.group(1)
        # fallback: plain email pattern in text
        plain = re.search(r'[\w.+\-]+@[\w.\-]+\.[a-z]{2,}', html, re.I)
        if plain and not EMAIL_FALSE_POSITIVES.search(plain.group(0)):
            return plain.group(0)
    except Exception:
        pass
    return "—"


# ── DuckDuckGo fallback ───────────────────────────────────────────────────────

SKIP_DOMAINS = [
    "yelp.com", "tripadvisor", "yellowpages", "google.com", "facebook.com",
    "instagram.com", "twitter.com", "tiktok.com", "linkedin.com",
    "thrillist.com", "timeout.com", "eater.com", "zagat.com",
    "azcentral.com", "usatoday.com", "buzzfeed.com", "huffpost.com",
    "nytimes.com", "forbes.com", "entrepreneur.com", "reddit.com",
    "nextdoor.com", "citysearch.com", "foursquare.com", "mapquest.com",
    "bbb.org", "chamberofcommerce.com", "angi.com", "thumbtack.com",
    "houzz.com", "homeadvisor.com", "angieslist.com",
]

ARTICLE_TITLE_RE = re.compile(
    r"^(\d+[\s\-]|best |top |guide |review |where |how |what |why |the best )",
    re.I,
)

ARTICLE_URL_RE = re.compile(
    r"/(best-|top-|guide|article|story|blog|list|review|news|feature|ranking)",
    re.I,
)


def ddg_search(query: str) -> str:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  DDG error: {e}", file=sys.stderr)
        return ""


def extract_ddg_results(html: str, limit: int = 8) -> list[dict]:
    results = []
    titles = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    snippets = re.findall(r'class="result__snippet">(.*?)</span>', html, re.S)
    seen_domains: set = set()
    for i, (url, title) in enumerate(titles):
        if len(results) >= limit:
            break
        title = re.sub(r"<[^>]+>", "", title).strip()
        snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip() if i < len(snippets) else ""
        if any(d in url for d in SKIP_DOMAINS):
            continue
        if ARTICLE_TITLE_RE.match(title):
            continue
        if ARTICLE_URL_RE.search(url):
            continue
        try:
            domain = urllib.parse.urlparse(url).netloc
        except Exception:
            domain = url
        if domain in seen_domains:
            continue
        seen_domains.add(domain)
        results.append({"title": title, "url": url, "snippet": snippet})
    return results


# ── Shared helpers ────────────────────────────────────────────────────────────

def find_email_in_snippet(snippet: str) -> str:
    match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", snippet)
    return match.group(0) if match else "—"


def find_phone_in_snippet(snippet: str) -> str:
    match = re.search(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", snippet)
    return match.group(0) if match else "—"


def web_weakness(url: str) -> str:
    u = url.lower()
    if not url or url == "—":
        return "**No website found** — best pitch"
    if "wix.com" in u or "wixsite" in u:
        return "Wix template — no SEO, no booking"
    if "squarespace" in u:
        return "Squarespace — likely no booking or local SEO"
    if "godaddy" in u:
        return "GoDaddy builder — outdated, poor mobile"
    if ".net" in u:
        return "Old .net domain — likely outdated site"
    if any(x in u for x in ["myshopify", "shopify"]):
        return "Shopify only — no content/social strategy"
    return "Has website — check for weak socials/reels"


def linkedin_search_url(business_name: str, city: str) -> str:
    query = urllib.parse.quote(f"{business_name} {city.split(',')[0]}")
    return f"https://www.linkedin.com/search/results/companies/?keywords={query}"


# ── Main research function ────────────────────────────────────────────────────

def research_niche(city: str, niche_key: str, osm_tags: list, ddg_query: str) -> list[dict]:
    city_name = city.split(",")[0]
    print(f"  [{niche_key}] Overpass: {city_name}", file=sys.stderr)

    elements = overpass_search(city_name, osm_tags, limit=15)
    time.sleep(2)

    leads = []
    for el in elements:
        parsed = parse_osm_element(el)
        if not parsed:
            continue
        # enrich email from website if OSM doesn't have one
        if parsed["email"] == "—" and parsed["url"] != "—":
            print(f"    scraping {parsed['url']} for email", file=sys.stderr)
            parsed["email"] = scrape_email_from_site(parsed["url"])
            time.sleep(0.5)
        parsed["linkedin"] = linkedin_search_url(parsed["name"], city)
        parsed["weakness"] = web_weakness(parsed["url"])
        leads.append(parsed)

    if leads:
        print(f"  [{niche_key}] {len(leads)} leads from Overpass", file=sys.stderr)
        return leads

    # fallback — DDG when Overpass returns nothing (sparse OSM coverage)
    print(f"  [{niche_key}] Overpass empty — falling back to DuckDuckGo", file=sys.stderr)
    query = f'independent {ddg_query} in "{city}" -chain -franchise'
    html = ddg_search(query)
    results = extract_ddg_results(html, limit=8)
    time.sleep(1)
    for r in results:
        url = r["url"] if r["url"].startswith("http") else "—"
        email = find_email_in_snippet(r["snippet"])
        if email == "—" and url != "—":
            email = scrape_email_from_site(url)
        leads.append({
            "name": r["title"],
            "url": url,
            "phone": find_phone_in_snippet(r["snippet"]),
            "email": email,
            "linkedin": linkedin_search_url(r["title"], city),
            "weakness": web_weakness(url),
        })
    print(f"  [{niche_key}] {len(leads)} leads from DuckDuckGo fallback", file=sys.stderr)
    return leads


# ── Report builder ────────────────────────────────────────────────────────────

def build_report(city: str, date: datetime.date) -> str:
    city_name = city.split(",")[0]
    lines = [f"# {city} Outreach Leads — {date.strftime('%B %d, %Y')}", ""]
    lines += [
        f"**Target:** Local service businesses in {city} with weak content/social presence  ",
        f"**Offer:** Content Sprint — brand spine + 15 reels + creator collab, 2-week trial  ",
        "",
    ]

    all_leads = []
    for niche_key, osm_tags, ddg_query in NICHES:
        leads = research_niche(city, niche_key, osm_tags, ddg_query)
        lines += [f"## {niche_key.replace('_', ' ').title()}", ""]
        lines += [f"*Pitch: {PITCH[niche_key]}*", ""]
        lines += ["| Business | Website | Phone | Email | LinkedIn | Web Issue |", "|---|---|---|---|---|---|"]
        for lead in leads:
            lines.append(
                f"| {lead['name']} | {lead['url']} | {lead['phone']} | {lead['email']} "
                f"| [Search]({lead['linkedin']}) | {lead['weakness']} |"
            )
            all_leads.append((niche_key, lead))
        lines.append("")

    lines += ["## Priority Send Order", ""]
    no_site  = [(k, l) for k, l in all_leads if "No website" in l["weakness"]]
    has_email = [(k, l) for k, l in all_leads if l["email"] != "—" and "No website" not in l["weakness"]]
    rest     = [(k, l) for k, l in all_leads if (k, l) not in no_site and (k, l) not in has_email]

    rank = 1
    for group in [no_site, has_email, rest]:
        for k, l in group:
            lines.append(f"{rank}. **{l['name']}** ({k}) — {l['weakness']}")
            rank += 1

    lines.append(EMAIL_TEMPLATE.format(niche="local businesses", city=city_name))
    return "\n".join(lines)


def main():
    today = datetime.date.today()
    city = pick_city(today)
    print(f"City today: {city}", file=sys.stderr)

    content = build_report(city, today)

    city_slug = city.split(",")[0].lower().replace(" ", "-")
    filename = f"outreach/leads-{city_slug}-{today.isoformat()}.md"

    os.makedirs("outreach", exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)

    print(f"Saved: {filename}", file=sys.stderr)
    print(filename)


if __name__ == "__main__":
    main()
