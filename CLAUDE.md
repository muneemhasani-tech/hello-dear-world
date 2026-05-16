# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Automated outreach pipeline for **NINE** — a creative agency (Bangladesh-based, international clients) specialising in motion graphics, branding, and influencer content for restaurants, health/wellness, FMCG, and events businesses. Two GitHub Actions workflows run on a schedule, scrape public data, and commit structured markdown files back to the repo. No external API keys or paid services are used anywhere.

## Running the scripts locally

```bash
# Research leads for today's city
python scripts/research_leads.py

# Analyse all leads files and produce a ranked report
python scripts/analyze_leads.py
```

Both scripts use Python 3.12+ stdlib only — no `pip install` needed.

Output files are printed to stdout (the filename); progress/errors go to stderr.

## Architecture

### Pipeline flow

```
Daily (7pm UTC)                Every 2 days (8pm UTC)
research_leads.py         →    analyze_leads.py
  picks city by date             reads outreach/leads-*.md
  scrapes DuckDuckGo HTML        fetches sitemaps (client + competitor)
  writes outreach/leads-         scores gap (0–100)
    {city}-{date}.md             maps to pricing tier
                                 writes analysis/
                                   client-ranking-{date}.md
```

### City rotation (`research_leads.py`)

City is selected by `date.toordinal() % len(CITIES)` — 50 Tier 2 cities across US, UK, and Australia (avoids over-served metros like NYC, London, Austin). Cities include Asheville NC, Brighton UK, Byron Bay AU, Boise ID, etc. Rotation is deterministic by date.

### Target niches

`research_leads.py` searches four niches per city:
- `restaurants` — independent restaurants, cafes, bistros
- `health_wellness` — wellness studios, supplement brands, spas
- `fmcg` — artisan food/drink producers, packaged goods brands
- `events` — event venues, wedding venues, planners

### Leads table format

Each leads file has columns: `Business | Website | Phone | Email | LinkedIn | Web Issue`

The LinkedIn column contains a pre-built company search URL for each lead. A separate "LinkedIn DM Targets" section at the bottom of manually-enriched files lists decision maker profiles with connection note + DM copy.

### Sitemap analysis (`analyze_leads.py`)

- Tries `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml`, and `robots.txt` Sitemap directives in order
- Scores each lead 0–100 based on page count vs competitor + missing key pages (booking, services, blog, gallery, contact)
- Maps score to pricing tier: Full Rebuild ($8k–$18k) → Growth → Upgrade → Quick-Win → SEO/Maintenance ($300–$800/mo)
- Competitor found via DuckDuckGo search, skipping aggregators (Yelp, TripAdvisor, etc.)
- Analysis output includes a LinkedIn column in the quick-reference table

### Output files

| Path | Written by | Content |
|---|---|---|
| `outreach/leads-{city}-{date}.md` | `research_leads.py` | Raw leads grouped by niche with pitch angles and LinkedIn search links |
| `analysis/client-ranking-{date}.md` | `analyze_leads.py` | Scored + ranked leads with pricing, competitor comparison, and first-email hooks |

## GitHub Actions

Both workflows have `workflow_dispatch` enabled — trigger manually from the Actions tab without waiting for the schedule.

The analysis workflow runs 1 hour after the leads workflow so fresh leads are always included.

## Daily workflow skills

Six skills are installed at `~/.claude/skills/` for the daily outreach loop:

| Skill | Trigger | Purpose |
|---|---|---|
| `morning` | `/morning` | Briefing: today's city, top 3 leads, LinkedIn DMs ready to send |
| `outreach` | `/outreach` | Drafts 5 personalised cold emails from today's leads file |
| `dm` | `/dm` | Drafts LinkedIn connection notes + follow-up DMs per decision maker |
| `reply` | `/reply [paste]` | Identifies pipeline stage from a lead's reply, drafts next message |
| `eod` | `/eod` | Scores day against targets, flags follow-ups, confirms tomorrow's city |
| `connect` | `/connect` | Walks through connecting any tool in NINE's stack |

Daily outreach targets: **30 businesses found / 20 emails sent / 20–40 LinkedIn connections / 5–10 chats started / 2–3 serious leads.**

## Agency context (for outreach copy)

- Lead with reels and case studies — never mention location unprompted (Proof > Nationality)
- First offer is always the **Content Sprint**: 2-week trial — brand spine + 15 reels + creator collab
- Pitch angle: businesses with stunning products but flat socials or fragmented UGC
- Decision makers to target: Owners, Founders, CMOs at 11–1000 employee companies
