#!/usr/bin/env python3
"""
NINE daily lead researcher and gap audit engine — stdlib only.
Finds local businesses, audits their digital/brand presence against
industry benchmarks, identifies gaps mapped to NINE services, and
writes ready-to-send cold outreach copy per lead.
"""

import datetime
import os
import re
import sys
import time
import urllib.parse
import urllib.request

CITIES = [
    "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
    "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX",
    "Jacksonville, FL", "Austin, TX", "Columbus, OH", "Charlotte, NC",
    "Indianapolis, IN", "San Francisco, CA", "Seattle, WA", "Denver, CO",
    "Nashville, TN", "Oklahoma City, OK", "El Paso, TX", "Portland, OR",
    "Las Vegas, NV", "Memphis, TN", "Louisville, KY", "Baltimore, MD",
    "Milwaukee, WI", "Albuquerque, NM", "Tucson, AZ", "Fresno, CA",
    "Sacramento, CA", "Mesa, AZ", "Atlanta, GA", "Miami, FL",
    "Minneapolis, MN", "New Orleans, LA", "Cleveland, OH", "Tampa, FL",
    "Pittsburgh, PA", "Raleigh, NC", "Kansas City, MO", "Virginia Beach, VA",
    "Omaha, NE", "Colorado Springs, CO", "Long Beach, CA", "Bakersfield, CA",
    "Aurora, CO", "Honolulu, HI", "Anaheim, CA", "Santa Ana, CA",
    "Corpus Christi, TX", "Riverside, CA",
]

NICHES = [
    ("restaurants",    "independent restaurant cafe bistro"),
    ("health_wellness","wellness studio spa supplement brand"),
    ("fmcg",           "artisan food drink producer packaged goods brand"),
    ("events",         "event venue wedding venue event planner"),
]

# Industry leaders used as benchmark references per niche
BENCHMARKS = {
    "restaurants":    ["Sweetgreen", "Erewhon", "Blank Street Coffee"],
    "health_wellness":["Equinox", "Seed Health", "Goop"],
    "fmcg":           ["Oatly", "Fly By Jing", "OffLimits Cereal"],
    "events":         ["Zola", "Peerspace", "The Knot"],
}

# NINE service definitions — keys used in gap triggers
SERVICES = {
    "branding": {
        "label": "Branding Design",
        "pitch": "a custom visual identity system — logo, colour, type, and brand guidelines that own a distinct place in the market",
    },
    "static_content": {
        "label": "Static Content Creation",
        "pitch": "social posts, ads, and editorial assets built to your brand — consistent, on-spec, and ready to publish",
    },
    "motion_video": {
        "label": "Motion Video Editing",
        "pitch": "reels and brand films edited to platform spec with motion hooks that drive engagement",
    },
    "motion_graphics": {
        "label": "2D / 3D Motion Graphics",
        "pitch": "animated explainers, product demos, and transitions that make your content stop the scroll",
    },
    "research_strategy": {
        "label": "Research & Strategy",
        "pitch": "a competitor audit and positioning roadmap — so the brand leads the category instead of following it",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

AGGREGATORS = {
    "yelp.com", "tripadvisor", "yellowpages", "google.com",
    "facebook.com", "instagram.com", "tiktok.com",
}


# ── Network helpers ───────────────────────────────────────────────────────────

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


def fetch_website(url: str) -> str:
    if not url or not url.startswith("http"):
        return ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.read().decode("utf-8", errors="ignore")[:60000]
    except Exception:
        return ""


def extract_results(html: str, limit: int = 8) -> list[dict]:
    results = []
    titles   = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    snippets = re.findall(r'class="result__snippet">(.*?)</span>', html, re.S)
    for i, (url, title) in enumerate(titles[:limit * 2]):
        if len(results) >= limit:
            break
        title   = re.sub(r"<[^>]+>", "", title).strip()
        snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip() if i < len(snippets) else ""
        if any(d in url for d in AGGREGATORS):
            continue
        results.append({"title": title, "url": url, "snippet": snippet})
    return results


# ── Signal detection ──────────────────────────────────────────────────────────

def detect_signals(url: str, html: str, snippet: str) -> dict:
    """Return a flat dict of brand/content presence signals."""
    body = (html + " " + snippet).lower()
    url_l = url.lower()

    return {
        "no_website": not url or url == "—",

        # Builder / template
        "template_builder": any(x in url_l or x in body for x in [
            "wix.com", "wixsite", "squarespace", "godaddy", "weebly",
            "jimdo", "data-wix", "squarespace-cdn", "sites.google",
        ]),
        "webflow": "webflow" in body,

        # Social
        "has_instagram": "instagram.com" in body,
        "has_tiktok":    "tiktok.com" in body,
        "has_youtube":   "youtube.com" in body,
        "has_linkedin":  "linkedin.com" in body,

        # Motion / video
        "has_video": any(x in body for x in [
            "youtube.com/embed", "vimeo.com", "<video", "video/mp4", "watch?v=",
        ]),
        "has_reels": "reels" in body or ("tiktok" in body and "video" in body),

        # Content
        "has_blog": any(x in body for x in ["/blog", "/news", "/journal", "/articles", "read more"]),

        # Conversion
        "has_booking": any(x in body for x in [
            "book now", "book a", "schedule", "reserve", "appointment",
            "calendly", "acuity", "booksy", "mindbody", "vagaro",
        ]),
        "has_ordering": any(x in body for x in [
            "order online", "order now", "doordash", "ubereats", "grubhub",
            "toast", "square online", "add to cart", "shop now",
        ]),

        # Brand depth
        "has_brand_story": any(x in body for x in [
            "our story", "about us", "our mission", "who we are", "founded",
        ]),

        # Contact
        "has_email": bool(re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", body)),
        "has_phone": bool(re.search(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}", body)),
    }


# ── Gap audit ─────────────────────────────────────────────────────────────────

def brand_health_score(signals: dict, niche: str) -> tuple[int, str]:
    if signals["no_website"]:
        return 1, "no website — invisible outside directories"

    score = 5
    notes = []

    if signals["template_builder"]:
        score -= 1
        notes.append("template builder")
    else:
        score += 1

    social = signals["has_instagram"] + signals["has_tiktok"] + signals["has_youtube"]
    if social == 0:
        score -= 1
        notes.append("no social presence")
    elif social >= 2:
        score += 1

    if signals["has_video"] or signals["has_reels"]:
        score += 1
    else:
        score -= 1
        notes.append("no video content")

    if signals["has_blog"]:
        score += 1

    if signals["has_brand_story"]:
        score += 1

    if niche == "restaurants" and not signals["has_ordering"]:
        score -= 1
        notes.append("no online ordering")
    elif niche == "health_wellness" and not signals["has_booking"]:
        score -= 1
        notes.append("no booking system")

    score = max(1, min(10, score))
    reason = "; ".join(notes) if notes else "functional baseline"
    return score, reason


def identify_gaps(signals: dict, niche: str) -> list[dict]:
    """Return up to 4 gaps, each with benchmark framing and NINE service keys."""
    if signals["no_website"]:
        return [{
            "gap": "No web presence",
            "detail": "No standalone website — the business is invisible outside directories and relies entirely on platforms it doesn't own.",
            "benchmark": f"{BENCHMARKS[niche][0]} drives the majority of discovery and conversions through its own site.",
            "services": ["branding", "static_content"],
        }]

    gaps = []

    if signals["template_builder"]:
        gaps.append({
            "gap": "Generic visual identity",
            "detail": "Site is running on a template platform. No ownable visual language — the brand is indistinguishable from hundreds of competitors using the same theme.",
            "benchmark": f"{BENCHMARKS[niche][0]} operates with a tight, custom visual system: distinct typeface, ownable colour palette, consistent image treatment across every touchpoint.",
            "services": ["branding"],
        })

    if not signals["has_video"] and not signals["has_reels"]:
        gaps.append({
            "gap": "No motion or video content",
            "detail": "No video on site, no reels linked from social. Motion content is now the primary conversion driver in this category — static-only brands are losing attention at the top of the funnel.",
            "benchmark": f"{BENCHMARKS[niche][1]} leads every campaign with short-form video. It accounts for the majority of their organic engagement and drives direct traffic back to the site.",
            "services": ["motion_video", "motion_graphics"],
        })

    social_count = signals["has_instagram"] + signals["has_tiktok"] + signals["has_youtube"]
    if social_count == 0:
        gaps.append({
            "gap": "No social content strategy",
            "detail": "No social channels linked from site. Content is not being used as a growth channel — all discovery relies on paid or passive word-of-mouth.",
            "benchmark": f"{BENCHMARKS[niche][0]} posts 4–7x per week across Instagram and TikTok, with each piece carrying consistent brand-level visual quality.",
            "services": ["static_content", "motion_video"],
        })
    elif social_count == 1:
        gaps.append({
            "gap": "Single-platform social presence",
            "detail": "Only one channel linked — limiting reach and content surface area. A brand that only appears on one platform looks like it's just getting started.",
            "benchmark": f"{BENCHMARKS[niche][0]} maintains a consistent brand presence across 3+ platforms, with content adapted per format.",
            "services": ["static_content"],
        })

    if niche == "restaurants" and not signals["has_ordering"]:
        gaps.append({
            "gap": "No online ordering",
            "detail": "No ordering system visible on site. Google Local pushes restaurants with direct online ordering higher in results — and customers who can't order at midnight go to whoever can.",
            "benchmark": f"{BENCHMARKS[niche][2]} drives a significant share of revenue through direct online ordering, bypassing aggregator fees entirely.",
            "services": ["research_strategy"],
        })

    if niche == "health_wellness" and not signals["has_booking"]:
        gaps.append({
            "gap": "No online booking",
            "detail": "No booking system visible. Someone who decides to sign up at 11pm has no way to convert — they wake up the next morning, forget, and your competitor gets them.",
            "benchmark": f"{BENCHMARKS[niche][0]} offers frictionless in-site booking with upsell prompts — their conversion rate reflects that.",
            "services": ["research_strategy"],
        })

    if niche == "fmcg" and not signals["has_blog"] and not signals["has_ordering"]:
        gaps.append({
            "gap": "No content or direct purchase path",
            "detail": "No blog, no editorial presence, no direct-to-consumer buying option. FMCG brands that don't own a content channel are fully dependent on retail placement.",
            "benchmark": f"{BENCHMARKS[niche][0]} built its brand almost entirely on content — editorial, video, and community — before retail caught up.",
            "services": ["static_content", "research_strategy"],
        })

    if niche == "events" and not signals["has_video"]:
        gaps.append({
            "gap": "No venue showcase content",
            "detail": "No video walkthroughs, photo galleries, or immersive content. Clients booking events are buying an experience they can't see — video is the closest thing to a site visit.",
            "benchmark": f"{BENCHMARKS[niche][1]} lets clients 'walk through' every space before enquiring — video is their primary lead qualifier.",
            "services": ["motion_video", "motion_graphics"],
        })

    if not signals["has_brand_story"]:
        gaps.append({
            "gap": "No brand narrative",
            "detail": "No 'About', founder story, or mission content anywhere on site. The brand has no human face — it's impossible to build trust or justify premium pricing without one.",
            "benchmark": f"{BENCHMARKS[niche][0]} leads with founder story and brand values, which supports both customer retention and higher price tolerance.",
            "services": ["branding", "research_strategy"],
        })

    return gaps[:4]


def service_labels(gaps: list[dict]) -> list[str]:
    seen, labels = set(), []
    for gap in gaps:
        for key in gap.get("services", []):
            if key not in seen and key in SERVICES:
                seen.add(key)
                labels.append(SERVICES[key]["label"])
    return labels


# ── Cold outreach copy ────────────────────────────────────────────────────────

def cold_email(name: str, city: str, niche: str, gaps: list[dict]) -> str:
    if not gaps:
        return ""

    top = gaps[0]
    city_name = city.split(",")[0]
    niche_label = niche.replace("_", " ")

    # Opening observation — specific to the top gap type, never generic
    g = top["gap"].lower()
    if "motion" in g or "video" in g:
        opener = (
            f"I was looking at {name}'s site — the product clearly has something worth showing. "
            f"But there's no video content anywhere, and that's the heaviest conversion driver "
            f"in {niche_label} right now."
        )
    elif "visual identity" in g or "generic" in g:
        opener = (
            f"I came across {name} while researching {niche_label} brands in {city_name}. "
            f"The offer looks solid — but the site is running on a template, which makes it "
            f"hard to own a distinct place in the market."
        )
    elif "social" in g:
        opener = (
            f"I was looking at {name}'s online presence — strong product, but there's no "
            f"content engine behind it. No social linked anywhere, which means the brand "
            f"has no organic discovery channel working for it."
        )
    elif "ordering" in g:
        opener = (
            f"Found {name} while researching {niche_label} businesses in {city_name}. "
            f"Great reviews — but there's no way to order directly from your site, which means "
            f"you're losing late-night decisions to competitors who do."
        )
    elif "booking" in g:
        opener = (
            f"Found {name} while looking at {niche_label} businesses in {city_name}. "
            f"Strong reputation — but there's no way to book directly from your site, which "
            f"means anyone who decides to commit outside business hours has no way to convert."
        )
    elif "narrative" in g or "story" in g:
        opener = (
            f"I was looking at {name}'s site. The business clearly has depth — but there's no "
            f"brand story, no founder angle, nothing that gives a new visitor a reason to choose "
            f"you over someone cheaper."
        )
    else:
        opener = (
            f"I came across {name} while researching {niche_label} brands in {city_name}. "
            f"{top['detail']}"
        )

    # Service pitch — use the first recommended service
    first_service_key = top["services"][0] if top["services"] else None
    service_pitch = SERVICES[first_service_key]["pitch"] if first_service_key else "creative production"

    return (
        f"**Subject:** {name} — one thing I noticed\n\n"
        f"Hi,\n\n"
        f"{opener}\n\n"
        f"{top['benchmark']}\n\n"
        f"We're NINE — a creative agency that works with {niche_label} brands on exactly this. "
        f"We'd build {service_pitch}, so you're not leaving that gap open while competitors close it.\n\n"
        f"Worth a 15-minute call this week?\n\n"
        f"[Your name]\nNINE"
    )


# ── Report assembly ───────────────────────────────────────────────────────────

def audit_lead(result: dict, city: str, niche: str) -> dict:
    url = result["url"] if result["url"].startswith("http") else "—"
    print(f"    Auditing: {url[:70]}", file=sys.stderr)
    html = fetch_website(url)
    time.sleep(0.5)

    signals = detect_signals(url, html, result["snippet"])
    score, score_reason = brand_health_score(signals, niche)
    gaps = identify_gaps(signals, niche)

    return {
        "name":         result["title"],
        "url":          url,
        "score":        score,
        "score_reason": score_reason,
        "gaps":         gaps,
        "services":     service_labels(gaps),
        "email":        cold_email(result["title"], city, niche, gaps),
        "has_email":    signals["has_email"],
        "has_phone":    signals["has_phone"],
    }


def format_lead_block(lead: dict, rank: int) -> list[str]:
    bar   = "█" * lead["score"] + "░" * (10 - lead["score"])
    lines = [
        f"### {rank}. {lead['name']}",
        f"**Website:** {lead['url']}  ",
        f"**Brand Health:** {lead['score']}/10 `{bar}`  ",
        f"**Weakness:** {lead['score_reason']}  ",
        f"**NINE Services:** {', '.join(lead['services']) if lead['services'] else '—'}  ",
        "",
    ]

    if lead["gaps"]:
        lines.append("**Gap Analysis:**")
        lines.append("")
        for gap in lead["gaps"]:
            lines += [
                f"**{gap['gap']}**",
                gap["detail"],
                f"*Benchmark: {gap['benchmark']}*",
                "",
            ]

    if lead["email"]:
        lines += [
            "**Cold Outreach Email — ready to send:**",
            "",
            lead["email"],
            "",
        ]

    lines += ["---", ""]
    return lines


def build_report(city: str, date: datetime.date) -> str:
    city_name = city.split(",")[0]
    lines = [
        f"# NINE Gap Audit — {city} / {date.strftime('%B %d, %Y')}",
        "",
        f"**Method:** Per-lead brand audit benchmarked against category leaders.  ",
        f"**Output:** Gap analysis + ready-to-send cold outreach per business.  ",
        "",
        "---",
        "",
    ]

    all_leads: list[tuple[str, dict]] = []

    for niche_key, niche_query in NICHES:
        query = f'independent {niche_query} in "{city}" -chain -franchise'
        print(f"  Searching [{niche_key}]: {query[:80]}", file=sys.stderr)
        html = ddg_search(query)
        results = extract_results(html, limit=6)
        time.sleep(1)

        niche_label  = niche_key.replace("_", " ").title()
        benchmarks   = " / ".join(BENCHMARKS.get(niche_key, []))
        lines += [
            f"## {niche_label}",
            f"*Benchmarked against: {benchmarks}*",
            "",
        ]

        if not results:
            lines += ["*No results returned for this niche — DDG may be throttling.*", "", "---", ""]
            continue

        leads = [audit_lead(r, city, niche_key) for r in results]
        for i, lead in enumerate(leads, 1):
            lines += format_lead_block(lead, i)
            all_leads.append((niche_key, lead))

    # Priority hit list — lowest score = most opportunity for NINE
    lines += [
        "## Priority Hit List",
        "",
        "*Ranked by gap opportunity — lowest brand health score first.*",
        "",
        "| # | Business | Niche | Score | Top Gap | NINE Services |",
        "|---|---|---|---|---|---|",
    ]
    sorted_leads = sorted(all_leads, key=lambda x: x[1]["score"])
    for rank, (niche_key, lead) in enumerate(sorted_leads[:12], 1):
        top_gap  = lead["gaps"][0]["gap"] if lead["gaps"] else "—"
        services = ", ".join(lead["services"][:2]) if lead["services"] else "—"
        lines.append(
            f"| {rank} | **{lead['name']}** | {niche_key.replace('_', ' ').title()} "
            f"| {lead['score']}/10 | {top_gap} | {services} |"
        )

    lines.append("")
    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today()
    city  = pick_city(today)
    print(f"City today: {city}", file=sys.stderr)

    content   = build_report(city, today)
    city_slug = city.split(",")[0].lower().replace(" ", "-")
    filename  = f"outreach/leads-{city_slug}-{today.isoformat()}.md"

    os.makedirs("outreach", exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)

    print(f"Saved: {filename}", file=sys.stderr)
    print(filename)


if __name__ == "__main__":
    main()
