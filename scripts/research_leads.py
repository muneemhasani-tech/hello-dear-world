#!/usr/bin/env python3
"""
Daily NINE lead researcher — no API keys required.

Improvements over v1:
  - Multiple targeted sub-queries per niche (5–6 each) to surface 10-15 leads
  - Visits actual business websites (homepage + /contact) to find emails
  - Exponential-backoff retry on DuckDuckGo rate limiting
  - Expanded SKIP_DOMAINS (booking platforms, review aggregators, directories)
  - Queries narrowed to NINE's target industries per the brand knowledge base:
      restaurants / cafés / bakeries / craft breweries
      med spas / day spas / boutique fitness / yoga / holistic wellness
      craft beer / artisan food / specialty supplements
      event venues / wedding venues
"""

import datetime
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# City rotation — 50 Tier 2 cities across US, UK, Australia
# ---------------------------------------------------------------------------

CITIES = [
    # US Tier 2
    "Asheville, NC", "Boise, ID", "Chattanooga, TN", "Greenville, SC",
    "Savannah, GA", "Fort Collins, CO", "Eugene, OR", "Spokane, WA",
    "Knoxville, TN", "Huntsville, AL", "Madison, WI", "Ann Arbor, MI",
    "Burlington, VT", "Charlottesville, VA", "Flagstaff, AZ", "Santa Fe, NM",
    "Bend, OR", "Fayetteville, AR", "Lexington, KY", "Columbia, SC",
    "Wilmington, NC", "Richmond, VA", "Tulsa, OK", "Des Moines, IA",
    "Grand Rapids, MI", "Dayton, OH", "Springfield, MO", "Peoria, IL",
    "Wichita, KS", "Little Rock, AR",
    # UK Tier 2
    "Brighton, UK", "Bristol, UK", "Edinburgh, UK", "Cardiff, UK",
    "Norwich, UK", "Exeter, UK", "Bath, UK", "York, UK",
    "Oxford, UK", "Coventry, UK",
    # Australia Tier 2
    "Byron Bay, Australia", "Noosa, Australia", "Hobart, Australia",
    "Geelong, Australia", "Launceston, Australia", "Cairns, Australia",
    "Townsville, Australia", "Wollongong, Australia",
    "Gold Coast, Australia", "Sunshine Coast, Australia",
]

# ---------------------------------------------------------------------------
# NICHES — each entry is (key, display_name, [sub_queries])
# Sub-queries are run sequentially; results are merged & de-duped until
# PER_NICHE_TARGET leads are collected for that niche.
# Queries are narrowed to NINE's primary target industries.
# ---------------------------------------------------------------------------

NICHES = [
    ("restaurants", "Restaurants & F&B", [
        "independent restaurant",
        "independent bistro cafe eatery",
        "independent bar grill cocktail bar",
        "independent bakery patisserie",
        "craft brewery taproom",
    ]),
    ("health_wellness", "Health & Wellness", [
        "medspa medical spa aesthetics",
        "day spa wellness spa",
        "yoga studio pilates studio barre",
        "boutique fitness gym personal training",
        "holistic wellness naturopath integrative health",
    ]),
    ("fmcg", "FMCG & Artisan Products", [
        "artisan food producer specialty food",
        "craft spirits distillery",
        "independent supplement nutrition brand",
    ]),
    ("events", "Events & Venues", [
        "independent event venue",
        "independent wedding venue",
    ]),
]

# How many leads to collect per niche (collect up to 2× this from DDG, trim later)
PER_NICHE_TARGET = 5

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Domains to skip — directories, aggregators, booking platforms, social media
SKIP_DOMAINS = [
    # Reviews / directories
    "yelp.com", "tripadvisor", "yellowpages", "google.com", "bbb.org",
    "chamberofcommerce.com", "citysearch.com", "foursquare.com",
    "mapquest.com", "bing.com", "yahoo.com", "yp.com", "manta.com",
    "alignable.com", "nextdoor.com", "patch.com", "localstack.com",
    # Social media
    "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
    "linkedin.com", "pinterest.com", "youtube.com", "snapchat.com",
    # Food aggregators
    "opentable.com", "resy.com", "doordash.com", "grubhub.com",
    "seamless.com", "ubereats.com", "toasttab.com", "allmenus.com",
    "menupages.com", "zomato.com", "eater.com", "thrillist.com",
    "timeout.com", "zagat.com",
    # Booking / wellness platforms
    "mindbodyonline.com", "vagaro.com", "booksy.com", "fresha.com",
    "classpass.com", "wellnessliving.com", "squareup.com",
    "styleseat.com", "boulevard.io",
    # Health directories
    "healthgrades.com", "zocdoc.com", "webmd.com", "vitals.com",
    # Wedding / events
    "weddingwire.com", "theknot.com", "eventbrite.com", "thumbtack.com",
    # Home services
    "angi.com", "homeadvisor.com", "angieslist.com", "houzz.com",
    # News / media
    "nytimes.com", "forbes.com", "entrepreneur.com", "usatoday.com",
    "buzzfeed.com", "huffpost.com", "reddit.com", "azcentral.com",
]

ARTICLE_TITLE_RE = re.compile(
    r"^(\d+[\s\-]|best |top |guide |review |where |how |what |why |the best )",
    re.I,
)
ARTICLE_URL_RE = re.compile(
    r"/(best-|top-|guide|article|story|blog|list|review|news|feature|ranking)",
    re.I,
)
EMAIL_RE = re.compile(r"[\w.\-+]+@[\w.\-]+\.\w{2,6}")
PHONE_RE = re.compile(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")

# Emails that look real but aren't contact addresses
EMAIL_SKIP = {
    "example.", "domain.", "test@", "@sentry", "noreply", "no-reply",
    "privacy@", "legal@", "abuse@", "@2x.", ".png@", ".jpg@", ".svg@",
    "support@wix", "support@squarespace", "support@godaddy",
    "@schema.org", "postmaster@",
}


# ---------------------------------------------------------------------------
# Network functions
# ---------------------------------------------------------------------------

def ddg_search(query: str, retries: int = 3) -> str:
    """Search DuckDuckGo HTML with exponential-backoff retry."""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                if "result__a" in html:
                    return html
                # Soft rate-limit: empty page returned
                wait = 2 ** (attempt + 1)
                print(
                    f"  DDG empty (attempt {attempt + 1}/{retries}), "
                    f"waiting {wait}s …",
                    file=sys.stderr,
                )
                time.sleep(wait)
        except urllib.error.HTTPError as e:
            wait = 2 ** (attempt + 1)
            print(
                f"  DDG HTTP {e.code} (attempt {attempt + 1}/{retries}), "
                f"waiting {wait}s …",
                file=sys.stderr,
            )
            time.sleep(wait)
        except Exception as e:
            print(f"  DDG error: {e}", file=sys.stderr)
            time.sleep(2)
    return ""


def fetch_page(url: str, timeout: int = 7) -> str:
    """Fetch a page and return up to 60 KB of text, or '' on any failure."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ct = resp.headers.get("Content-Type", "")
            if "html" not in ct and "text" not in ct:
                return ""
            return resp.read().decode("utf-8", errors="ignore")[:60_000]
    except Exception:
        return ""


def scrape_email_from_site(base_url: str) -> str:
    """
    Visit the business homepage, then /contact or /contact-us,
    and return the first valid-looking email address found.
    """
    if not base_url.startswith("http"):
        return "—"

    parsed = urllib.parse.urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    for page in [base_url, f"{root}/contact", f"{root}/contact-us"]:
        html = fetch_page(page)
        if not html:
            continue
        # Strip tags for cleaner matching
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"&#?\w+;", " ", text)
        for m in EMAIL_RE.findall(text):
            if not any(skip in m.lower() for skip in EMAIL_SKIP):
                return m

    return "—"


# ---------------------------------------------------------------------------
# DDG result parsing
# ---------------------------------------------------------------------------

def extract_results(html: str, limit: int = 10) -> list[dict]:
    """Parse DDG HTML into a filtered, de-duped list of result dicts."""
    results: list[dict] = []
    titles = re.findall(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S
    )
    snippets = re.findall(r'class="result__snippet">(.*?)</span>', html, re.S)

    seen_domains: set[str] = set()
    for i, (url, title) in enumerate(titles):
        if len(results) >= limit:
            break
        title = re.sub(r"<[^>]+>", "", title).strip()
        snippet = (
            re.sub(r"<[^>]+>", "", snippets[i]).strip()
            if i < len(snippets)
            else ""
        )
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
        results.append({"title": title, "url": url, "snippet": snippet, "domain": domain})

    return results


# ---------------------------------------------------------------------------
# Lead enrichment helpers
# ---------------------------------------------------------------------------

def find_email_in_snippet(snippet: str) -> str:
    m = EMAIL_RE.search(snippet)
    if m and not any(skip in m.group(0).lower() for skip in EMAIL_SKIP):
        return m.group(0)
    return "—"


def find_phone(snippet: str) -> str:
    m = PHONE_RE.search(snippet)
    return m.group(0) if m else "—"


def web_weakness(url: str, snippet: str) -> str:
    u = (url or "").lower()
    if not u or u == "—":
        return "**No website found** — best pitch"
    if "wix.com" in u or "wixsite" in u:
        return "Wix template — generic, no SEO, no booking"
    if "squarespace" in u:
        return "Squarespace — likely no booking or local SEO"
    if "godaddy" in u:
        return "GoDaddy builder — outdated, poor mobile"
    if ".net" in u and not any(x in u for x in ["fitness", "studio", "salon", "clinic"]):
        return "Old .net domain — likely outdated site"
    s = snippet.lower()
    if not any(w in s for w in ["book", "schedule", "reserv", "appoint"]):
        return "No online booking mentioned — clear gap"
    return "Check site for booking/SEO gaps"


def linkedin_search_url(name: str, city: str) -> str:
    q = urllib.parse.quote(f"{name} {city.split(',')[0]}")
    return f"https://www.linkedin.com/search/results/companies/?keywords={q}"


# ---------------------------------------------------------------------------
# Core research function
# ---------------------------------------------------------------------------

def research_niche(
    city: str,
    niche_key: str,
    sub_queries: list[str],
    target: int = PER_NICHE_TARGET,
) -> list[dict]:
    """
    Run multiple targeted sub-queries for one niche, collect up to `target`
    unique business leads, then enrich each with an email scraped from the
    actual business website.
    """
    seen_domains: set[str] = set()
    raw: list[dict] = []

    for sub_q in sub_queries:
        if len(raw) >= target * 2:
            break
        # Quoted sub-query forces phrase match; -chain/-franchise/-directory
        # reduces aggregator noise
        query = f'"{sub_q}" in "{city}" -chain -franchise -directory'
        print(f"  Searching: {query}", file=sys.stderr)
        html = ddg_search(query)
        for r in extract_results(html, limit=10):
            if r["domain"] not in seen_domains:
                seen_domains.add(r["domain"])
                raw.append(r)
        time.sleep(1.5)  # polite gap between DDG requests

    leads: list[dict] = []
    for r in raw[:target]:
        site = r["url"] if r["url"].startswith("http") else "—"

        # 1. Fast path — email already in DDG snippet
        email = find_email_in_snippet(r["snippet"])

        # 2. Slow path — visit the actual site
        if email == "—" and site != "—":
            print(f"  Scraping: {site}", file=sys.stderr)
            email = scrape_email_from_site(site)

        leads.append({
            "name": r["title"],
            "url": site,
            "phone": find_phone(r["snippet"]),
            "email": email,
            "linkedin": linkedin_search_url(r["title"], city),
            "weakness": web_weakness(site, r["snippet"]),
        })

    return leads


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

PITCH = {
    "restaurants":   "Stunning food, flat socials — reels + a Google-optimised site turns browsers into bookings",
    "health_wellness": "Wellness is booming but their content doesn't show it — motion-heavy reels + influencer collab fills the gap",
    "fmcg":          "Great product, no visual identity online — brand spine + creator UGC puts product in front of buyers",
    "events":        "Event venues live and die by scroll-stopping visuals — no reel strategy = invisible to couples/planners searching now",
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


def build_report(city: str, date: datetime.date) -> str:
    city_name = city.split(",")[0]
    lines = [f"# {city} Outreach Leads — {date.strftime('%B %d, %Y')}", ""]
    lines += [
        f"**Target:** Local service businesses in {city} with weak web presence  ",
        f"**Qualifier:** No online booking, outdated site, no SEO, Wix/GoDaddy templates  ",
        "",
    ]

    all_leads: list[tuple[str, dict]] = []

    for niche_key, niche_display, sub_queries in NICHES:
        leads = research_niche(city, niche_key, sub_queries)
        lines += [f"## {niche_display}", ""]
        lines += [f"*Pitch: {PITCH[niche_key]}*", ""]
        lines += [
            "| Business | Website | Phone | Email | LinkedIn | Web Issue |",
            "|---|---|---|---|---|---|",
        ]
        for lead in leads:
            lines.append(
                f"| {lead['name']} | {lead['url']} | {lead['phone']} "
                f"| {lead['email']} | [Search]({lead['linkedin']}) "
                f"| {lead['weakness']} |"
            )
            all_leads.append((niche_key, lead))
        lines.append("")

    # Priority order: no website first, then confirmed email, then rest
    no_site  = [(k, l) for k, l in all_leads if "No website" in l["weakness"]]
    has_email = [
        (k, l) for k, l in all_leads
        if l["email"] != "—" and "No website" not in l["weakness"]
    ]
    rest = [
        (k, l) for k, l in all_leads
        if (k, l) not in no_site and (k, l) not in has_email
    ]

    lines += ["## Priority Send Order", ""]
    rank = 1
    for group in [no_site, has_email, rest]:
        for k, l in group:
            lines.append(f"{rank}. **{l['name']}** ({k}) — {l['weakness']}")
            rank += 1

    lines.append(EMAIL_TEMPLATE.format(niche="local businesses", city=city_name))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
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


def pick_city(date: datetime.date) -> str:
    return CITIES[date.toordinal() % len(CITIES)]


if __name__ == "__main__":
    main()
