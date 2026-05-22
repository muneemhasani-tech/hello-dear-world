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
| `audit/log.md` | `/audit` skill | Appended daily — scores, issues, and tomorrow's fixes across all 6 audit areas |
| `crm/week-{YYYY}-W{NN}.md` | `/crm` skill (via `/eod`) | Weekly lead tracker — all pipeline activity for the week |
| `crm/monthly-{YYYY-MM}.md` | `crm_merge.py` | Monthly CRM report — pipeline funnel, revenue forecast, niche + city breakdown |
| `NINE-OS/system-prompt.md` | Drive sync (manual) | Claude system prompt — NINE identity, services, tasks, constraints |

System prompt: ./NINE-OS/system-prompt.md

## GitHub Actions

All workflows have `workflow_dispatch` enabled — trigger manually from the Actions tab without waiting for the schedule.

The analysis workflow runs 1 hour after the leads workflow so fresh leads are always included.

The CRM merge workflow runs on the 1st of each month at 9am UTC. Trigger it manually with optional `year` and `month` inputs to regenerate any month.

## Daily workflow skills

Eight skills are installed at `~/.claude/skills/` for the daily outreach loop:

| Skill | Trigger | Purpose |
|---|---|---|
| `morning` | `/morning` | Briefing: today's city, top 3 leads, LinkedIn DMs ready to send |
| `outreach` | `/outreach` | Drafts 5 personalised cold emails from today's leads file |
| `dm` | `/dm` | Drafts LinkedIn connection notes + follow-up DMs per decision maker |
| `reply` | `/reply [paste]` | Identifies pipeline stage from a lead's reply, drafts next message |
| `post` | `/post [company]` | Generates a platform-specific prompt + reference image brief + company data card for a lead who replied. Asks which platform (Higgsfield, Midjourney, Runway, Firefly) before generating |
| `crm` | `/crm` | Logs or updates leads in the current week's CRM file; shows pipeline summary when called standalone |
| `eod` | `/eod` | Scores day against targets, flags follow-ups, confirms tomorrow's city — then auto-triggers /crm and /audit |
| `audit` | `/audit` | Scores the day across 6 areas (1–5), logs mistakes, writes tomorrow's fix list, appends to audit/log.md |
| `connect` | `/connect` | Walks through connecting any tool in NINE's stack |

Daily sequence: `/morning` → `/outreach` → `/dm` → `/reply [paste]` → `/post [company]` → `/eod` → `/crm` (auto) → `/audit` (auto)

### CRM system

Weekly files (`crm/week-{YYYY}-W{NN}.md`) are created and updated automatically during `/eod`. Each lead touched that day gets a row with stage, last action, next action, and value.

Monthly merge runs on the 1st via GitHub Actions (`crm_merge.py`). To generate manually:
```bash
python scripts/crm_merge.py 2026 5   # for May 2026
```

Daily outreach targets: **30 businesses found / 20 emails sent / 20–40 LinkedIn connections / 5–10 chats started / 2–3 serious leads.**

## Knowledge skills

Six knowledge skills are installed at `~/.claude/skills/` and trigger automatically on relevant questions:

| Skill | Triggers on |
|---|---|
| `claude-101` | Claude features, projects, artifacts, research mode, getting better results |
| `claude-api` | Building with the API, automation, tool use, RAG, pipelines, structured output |
| `mcp-intro` | Connecting Claude to external tools via MCP, CRM/scraper integrations |
| `agent-skills` | Writing SKILL.md files, encoding SOPs as skills, skill triggers |
| `subagents` | Delegating to subagents, parallel tasks, multi-step workflow automation |
| `ai-fluency` | Explaining AI to clients, 4D Framework, ethical AI, client education materials |

## Agency context (for outreach copy)

- Lead with reels and case studies — never mention location unprompted (Proof > Nationality)
- First offer is always the **Content Sprint**: 2-week trial — brand spine + 15 reels + creator collab
- Pitch angle: businesses with stunning products but flat socials or fragmented UGC
- Decision makers to target: Owners, Founders, CMOs at 11–1000 employee companies

---

## NINE-OS: Full Identity Sync
Last updated: 2026-05-22

### Operator
Name: Syed Tahsin
Agency: NINE (The Corp Nine)
Email: tahsin@thecorpnine.com
Backup: corp.nine4@gmail.com
Timezone: GMT+6 (Bangladesh)
Daily routine: 2:15–2:45pm GMT+6 — NINE Daily Outreach Checklist

### Revenue Target
$10,000–$15,000 MRR at 60–70% gross margins

### Active Client Projects
Kaizen Connects Limited
- Japanese skincare, Bangladesh market
- Status: active (Jan–Feb 2026)
- Docs in Google Drive

SAVEE
- Skincare brand, Bangladesh
- Status: active (Feb 2026)

US Cold Outreach Pipeline
- Cities: Whitefish MT + 3 others
- Named target: Hellroaring Saloon (Whitefish MT)
- Status: active daily

### Team
Md. Saif Uz Zaman — FMCG/commercial background, Bangladesh
Role: hire candidate or contractor (confirm with Nine)

### Active Tools
Apollo — prospecting
Bright Data — scraping and research
Mailsuite — email tracking (upgraded)
Supermetrics — analytics (trial, started 2026-05-20)
Gmail — outreach sending
Google Drive — all docs and SOPs
Google Calendar — daily routine trigger

### Key Google Drive Doc IDs
Daily Workflow Reference: 11CqndlryByRO9N2gIzr-vgq8Fp3HZPw1b0qc8-BFKnU
Tools & Plugins Reference: 12dhOQoorZIbHgsishN22l-Cd_GUvXqu0DtVBX5qWMP8
Pipeline Backlog (4 cities): 1F_A_tfrarrJLgdwdWGBD8WFx8EvL_9KejnGxhtyumVQ
Company Tracker Whitefish: 1UiNVdDdAoQ9XG1aA9Zi6_MTlNHNEE-GipW7zbfYeD_g
Daily Work Log Whitefish: 1mSEoWNS9-5rKdvwFuWi0ApdebQ9DbqbrgfNrCG1_5ww
Claude System Prompt doc: 15xi5JBIZ6spteYjYJ63zxXWFrv1Lg4HzIA3PxRociaA
Pricing Table: 1THag3wt_ENRNwpDgnh1TM4jPln0CrFVX7jIVhUhfsS8

### What GitHub Actions Produce Daily
outreach/leads-{city}-{date}.md — scraped leads
analysis/client-ranking-{date}.md — scored opportunities
crm/monthly-{YYYY}-{MM}.md — pipeline rollup (1st of month)

### Critical Fixes Still Needed
1. All 15 NINE skill files missing from ~/.claude/skills/
2. Phoenix leads scraper pulling articles not businesses
3. export_notebook_knowledge.py script does not exist
4. CRM week files never created — monthly merge has nothing to merge
5. Claude system prompt in Drive not connected to Claude Code
