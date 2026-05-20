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

`research_leads.py` and `analyze_leads.py` require `pip install -r requirements.txt` and `playwright install chromium` (for the NotebookLM browser auth path). `crm_merge.py` remains stdlib-only.

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
