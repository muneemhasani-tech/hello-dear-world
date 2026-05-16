# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Automated outreach pipeline for **NINE** — a web design and digital marketing agency. Two GitHub Actions workflows run on a schedule, scrape public data, and commit structured markdown files back to the repo. No external API keys or paid services are used anywhere.

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

City is selected by `date.toordinal() % len(CITIES)` — a 50-city list that cycles deterministically. NYC was the seed run (May 16 2026); next is Los Angeles.

### Sitemap analysis (`analyze_leads.py`)

- Tries `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml`, and `robots.txt` Sitemap directives in order
- Scores each lead 0–100 based on page count vs competitor + missing key pages (booking, services, blog, gallery, contact)
- Maps score to pricing tier: Full Rebuild ($8k–$18k) → Growth → Upgrade → Quick-Win → SEO/Maintenance ($300–$800/mo)
- Competitor found via DuckDuckGo search, skipping aggregators (Yelp, TripAdvisor, etc.)

### Output files

| Path | Written by | Content |
|---|---|---|
| `outreach/leads-{city}-{date}.md` | `research_leads.py` | Raw leads grouped by niche with pitch angles |
| `analysis/client-ranking-{date}.md` | `analyze_leads.py` | Scored + ranked leads with pricing, competitor comparison, and first-email hooks |

## GitHub Actions

Both workflows have `workflow_dispatch` enabled — trigger manually from the Actions tab without waiting for the schedule.

The analysis workflow runs 1 hour after the leads workflow so fresh leads are always included.

## Skills installed

`~/.claude/skills/connect/SKILL.md` — `/connect` skill for setting up NINE's tool stack (Gmail MCP, Google Drive MCP, Calendar MCP, Tavily, Chrome extensions, Apps Script integrations). Run `/connect` to walk through connecting any tool.
