# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Automated outreach pipeline for **NINE** — a creative agency (Bangladesh-based, international clients) specialising in motion graphics, branding, and influencer content for restaurants, health/wellness, FMCG, and events businesses. GitHub Actions workflows run on a schedule, scrape public data, and commit structured markdown files back to the repo. No external API keys or paid services are used anywhere.

## Running the scripts locally

```bash
# Research leads for today's city
python scripts/research_leads.py

# Generate monthly CRM report (defaults to current month, or previous month if run on the 1st)
python scripts/crm_merge.py

# Generate for a specific month
python scripts/crm_merge.py 2026 5   # May 2026
```

Both scripts use Python 3.12+ stdlib only — no `pip install` needed.

Output filename is printed to stdout; progress/errors go to stderr.

## Architecture

### Pipeline flow

```
Daily (7pm UTC)                Monthly (9am UTC, 1st of month)
research_leads.py         →    crm_merge.py
  picks city by date             reads crm/week-*.md files
  scrapes DuckDuckGo HTML        deduplicates leads by business name
  writes outreach/leads-         (keeps most advanced pipeline stage)
    {city}-{date}.md             writes crm/monthly-{YYYY-MM}.md
```

### City rotation (`research_leads.py`)

City is selected by `date.toordinal() % len(CITIES)` — 50 US cities. Rotation is deterministic by date.

### Target niches

`research_leads.py` searches four niches per city, benchmarked against category leaders:

| Niche | Search terms | Benchmarks |
|---|---|---|
| `restaurants` | independent restaurant, cafe, bistro | Sweetgreen, Erewhon, Blank Street Coffee |
| `health_wellness` | wellness studio, spa, supplement brand | Equinox, Seed Health, Goop |
| `fmcg` | artisan food/drink producer, packaged goods brand | Oatly, Fly By Jing, OffLimits Cereal |
| `events` | event venue, wedding venue, event planner | Zola, Peerspace, The Knot |

### Per-lead gap audit

For each business found, the script fetches the homepage and runs a signal-based audit:

**Brand health score (1–10)** — heuristic based on: template builder detection, social channel presence, video/motion content, blog/editorial, booking or ordering system, brand narrative.

**Gap identification** — up to 4 gaps per lead, each with:
- Specific detail (what's missing and why it costs them)
- Competitor benchmark (what a category leader does instead)
- NINE services mapped to that gap

**NINE services triggered by gaps:**
- `Branding Design` — template builders, no ownable visual identity
- `Static Content Creation` — no social presence or single-platform
- `Motion Video Editing` / `2D-3D Motion Graphics` — no video or reels anywhere
- `Research & Strategy` — no ordering/booking, unclear positioning, no brand narrative

**Cold outreach email** — generated per lead, ready to send with zero editing. Opens with a specific observation about that business's gap (not a generic intro), frames the benchmark, pitches the relevant NINE service, and closes with a low-friction CTA.

### Output format

Each leads file is a strategic gap audit report — one section per niche, one detailed block per business, then a **Priority Hit List** table ranked by brand health score (lowest score = most opportunity for NINE).

### CRM merge (`crm_merge.py`)

- Reads `crm/week-{YYYY}-W{NN}.md` files where any day of the ISO week falls in the target month
- Parses the Lead Tracker table (9 columns: Business | City | Niche | Contact | Stage | Last Action | Next Action | Value | Notes)
- Deduplicates by business name, keeping the most advanced pipeline stage
- Outputs pipeline funnel, revenue forecast (30–70% probability on warm+ leads), niche performance, top cities, and full lead tracker

### Pipeline stages (in order)

`Found → Emailed → DM'd → Replied → Warm → Call Booked → Proposal Sent → Won → Lost`

### Pricing tiers (used in revenue estimates)

| Tier | Midpoint used |
|---|---|
| Full Rebuild | $13,000 |
| Growth Package | $6,000 |
| Upgrade Package | $3,000 |
| Quick-Win Package | $1,400 |
| Maintenance/SEO | $550 |

### Output files

| Path | Written by | Content |
|---|---|---|
| `outreach/leads-{city}-{date}.md` | `research_leads.py` | Raw leads grouped by niche with pitch angles and priority order |
| `crm/week-{YYYY}-W{NN}.md` | `/crm` skill (via `/eod`) | Weekly lead tracker — all pipeline activity for the week |
| `crm/monthly-{YYYY-MM}.md` | `crm_merge.py` | Monthly CRM report — pipeline funnel, revenue forecast, niche + city breakdown |
| `audit/log.md` | `/audit` skill | Appended daily — scores, issues, and tomorrow's fixes across all 6 audit areas |

## GitHub Actions

Both workflows have `workflow_dispatch` enabled — trigger manually from the Actions tab without waiting for the schedule.

- `daily-leads.yml` — runs `research_leads.py` at 7pm UTC daily, commits to `outreach/`
- `crm-monthly.yml` — runs `crm_merge.py` at 9am UTC on the 1st of each month, commits to `crm/monthly-*.md`; accepts optional `year` and `month` inputs for manual regeneration

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

Weekly CRM files (`crm/week-{YYYY}-W{NN}.md`) are created and updated automatically during `/eod`. Each lead touched that day gets a row with stage, last action, next action, and value.

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
