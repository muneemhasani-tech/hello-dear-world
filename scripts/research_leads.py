#!/usr/bin/env python3
"""
Daily NINE lead researcher — no API keys required.
Scrapes DuckDuckGo HTML + public business directories to find local service
businesses with weak web presence, then writes a structured leads file.
"""

import datetime
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

NICHES = [
    ("restaurants", "independent restaurant cafe bistro bar food"),
    ("health_wellness", "health wellness supplement nutrition studio spa"),
    ("fmcg", "food brand packaged goods artisan producer local product"),
    ("events", "event venue wedding venue event planner"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

PITCH = {
    "restaurants":    "Stunning food, flat socials — reels + a Google-optimised site turns browsers into bookings",
    "health_wellness": "Wellness is booming but their content doesn't show it — motion-heavy reels + influencer collab fills the gap",
    "fmcg":           "Great product, no visual identity online — brand spine + creator UGC puts product in front of buyers",
    "events":         "Event venues live and die by scroll-stopping visuals — no reel strategy = invisible to the couples/planners searching now",
}

EMAIL_TEMPLATE = """---

## Email Template

**Subject:** Quick question about [Business Name]'s website

Hi [Name],

I came across [Business Name] while looking at {niche} in {city} — great reviews.

One thing I noticed: [specific issue — e.g., no online booking / site doesn't rank on Google].

We help local businesses in {city} fix this — usually a quick update that brings in more customers without paid ads.

Worth a 10-minute chat this week?

[Your name]
NINE
"""


def pick_city(date: datetime.date) -> str:
    return CITIES[date.toordinal() % len(CITIES)]


def ddg_search(query: str) -> str:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  search error: {e}", file=sys.stderr)
        return ""


def extract_results(html: str, limit: int = 8) -> list[dict]:
    results = []
    # DuckDuckGo HTML result titles are in <a class="result__a">
    titles = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    snippets = re.findall(r'class="result__snippet">(.*?)</span>', html, re.S)

    for i, (url, title) in enumerate(titles[:limit]):
        title = re.sub(r"<[^>]+>", "", title).strip()
        snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip() if i < len(snippets) else ""
        # skip aggregator sites — we want direct business pages
        if any(d in url for d in ["yelp.com", "tripadvisor", "yellowpages", "google.com", "facebook.com"]):
            continue
        results.append({"title": title, "url": url, "snippet": snippet})

    return results


def find_email(snippet: str, url: str) -> str:
    match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", snippet)
    return match.group(0) if match else "—"


def find_phone(snippet: str) -> str:
    match = re.search(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", snippet)
    return match.group(0) if match else "—"


def web_weakness(url: str, snippet: str) -> str:
    url_lower = url.lower()
    if not url or url == "—":
        return "**No website found** — best pitch"
    if "wix.com" in url_lower or "wixsite" in url_lower:
        return "Wix template — generic, no SEO, no booking"
    if "squarespace" in url_lower:
        return "Squarespace template — likely no booking or local SEO"
    if "godaddy" in url_lower:
        return "GoDaddy builder — outdated, poor mobile"
    if ".net" in url_lower and not any(x in url_lower for x in ["fitness", "studio", "salon"]):
        return "Old .net domain — likely outdated site"
    if "booking" not in snippet.lower() and "schedule" not in snippet.lower():
        return "No online booking mentioned — clear gap"
    return "Check site for booking/SEO gaps"


def linkedin_search_url(business_name: str, city: str) -> str:
    city_name = city.split(",")[0]
    query = urllib.parse.quote(f"{business_name} {city_name}")
    return f"https://www.linkedin.com/search/results/companies/?keywords={query}"


def research_niche(city: str, niche_key: str, niche_query: str) -> list[dict]:
    query = f'independent {niche_query} in "{city}" -chain -franchise'
    print(f"  Searching: {query}", file=sys.stderr)
    html = ddg_search(query)
    results = extract_results(html, limit=8)
    time.sleep(1)

    leads = []
    for r in results:
        leads.append({
            "name": r["title"],
            "url": r["url"] if r["url"].startswith("http") else "—",
            "phone": find_phone(r["snippet"]),
            "email": find_email(r["snippet"], r["url"]),
            "linkedin": linkedin_search_url(r["title"], city),
            "weakness": web_weakness(r["url"], r["snippet"]),
        })
    return leads


def build_report(city: str, date: datetime.date) -> str:
    city_name = city.split(",")[0]
    lines = [f"# {city} Outreach Leads — {date.strftime('%B %d, %Y')}", ""]
    lines += [
        f"**Target:** Local service businesses in {city} with weak web presence  ",
        f"**Qualifier:** No online booking, outdated site, no SEO, Wix/GoDaddy templates  ",
        "",
    ]

    all_leads = []
    for niche_key, niche_query in NICHES:
        leads = research_niche(city, niche_key, niche_query)
        lines += [f"## {niche_key.title()}", ""]
        lines += [f"*Pitch: {PITCH[niche_key]}*", ""]
        lines += ["| Business | Website | Phone | Email | LinkedIn | Web Issue |", "|---|---|---|---|---|---|"]
        for lead in leads:
            lines.append(
                f"| {lead['name']} | {lead['url']} | {lead['phone']} | {lead['email']} | [Search]({lead['linkedin']}) | {lead['weakness']} |"
            )
            all_leads.append((niche_key, lead))
        lines.append("")

    # Priority order — no-website leads first, then email-available leads
    lines += ["## Priority Send Order", ""]
    no_site = [(k, l) for k, l in all_leads if "No website" in l["weakness"]]
    has_email = [(k, l) for k, l in all_leads if l["email"] != "—" and "No website" not in l["weakness"]]
    rest = [(k, l) for k, l in all_leads if (k, l) not in no_site and (k, l) not in has_email]

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
