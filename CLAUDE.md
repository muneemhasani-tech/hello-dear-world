# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Automated outreach pipeline for **NINE** — a creative agency (Bangladesh-based, international clients) specialising in motion graphics, branding, and influencer content for restaurants, health/wellness, FMCG, and events businesses. GitHub Actions workflows run on a schedule, scrape public data, and commit structured markdown files back to the repo.

## Running the scripts locally

```bash
# Research leads for today's city
python scripts/research_leads.py

# Analyse all leads files and produce a ranked report
python scripts/analyze_leads.py

# Export NINE brand knowledge from NotebookLM to knowledge/nine-brand-knowledge.md
# Requires: pip install "notebooklm-py[browser]" && playwright install chromium
# Requires: NOTEBOOKLM_STORAGE_STATE env var (full JSON from browser storage)
python scripts/export_notebook_knowledge.py

# Generate monthly CRM report manually
python scripts/crm_merge.py 2026 5   # year month
```

`research_leads.py`, `analyze_leads.py`, and `crm_merge.py` use Python 3.12+ stdlib only — no `pip install` needed. `export_notebook_knowledge.py` and the NotebookLM hook in `analyze_leads.py` require `notebooklm-py[browser]` + Playwright (optional — pipeline degrades gracefully without it).

Output files are printed to stdout (the filename); progress/errors go to stderr.

## Branch structure

- **`claude/automated-outreach-system-FqALG`** — active development branch; all script changes go here
- **`claude/new-session-467CY`** — default branch; scheduled GitHub Actions runs execute from here; workflow files are kept in sync between both branches

When pushing changes: push to `claude/automated-outreach-system-FqALG`. Mirror workflow file changes to `claude/new-session-467CY` via GitHub MCP (`mcp__github__push_files`) so they appear in the Actions sidebar.

## Architecture

### Pipeline flow

```
Daily (7pm UTC)                Every 2 days (8pm UTC)        1st of month (9am UTC)
research_leads.py         →    analyze_leads.py          →   crm_merge.py
  picks city by date             reads outreach/leads-*.md     reads crm/week-*.md
  scrapes DuckDuckGo HTML        fetches sitemaps               deduplicates leads
  writes outreach/leads-         queries NotebookLM for         writes crm/monthly-
    {city}-{date}.md             brand-voice email hooks          {YYYY-MM}.md
                                 scores gap (0–100)
                                 writes analysis/
                                   client-ranking-{date}.md

Manual trigger only:
export_notebook_knowledge.py
  queries 15 sections from NINE NotebookLM notebook
  writes knowledge/nine-brand-knowledge.md
```

### City rotation (`research_leads.py`)

City is selected by `date.toordinal() % len(CITIES)` — 50 Tier 2 cities across US, UK, and Australia (avoids over-served metros like NYC, London, Austin). Rotation is deterministic by date.

### Target niches

`research_leads.py` searches four niches per city: `restaurants`, `health_wellness`, `fmcg`, `events`.

### Leads table format

Each leads file has columns: `Business | Website | Phone | Email | LinkedIn | Web Issue`

The LinkedIn column contains a pre-built company search URL for each lead. A separate "LinkedIn DM Targets" section at the bottom of manually-enriched files lists decision maker profiles with connection note + DM copy.

### Sitemap analysis (`analyze_leads.py`)

- Tries `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml`, and `robots.txt` Sitemap directives in order
- Scores each lead 0–100 based on page count vs competitor + missing key pages (booking, services, blog, gallery, contact)
- Maps score to pricing tier: Full Rebuild ($8k–$18k) → Growth → Upgrade → Quick-Win → SEO/Maintenance ($300–$800/mo)
- Competitor found via DuckDuckGo search, skipping aggregators (Yelp, TripAdvisor, etc.)
- Before drafting email hooks, optionally calls `notebooklm_context.py` if `NOTEBOOKLM_STORAGE_STATE` is set

### NotebookLM integration

`scripts/notebooklm_context.py` is a utility module imported by `analyze_leads.py`. It queries the NINE NotebookLM notebook (`2d54d3d9-bc8d-42b7-8db7-1ac2dee912a7`) for brand-voice hooks before each email draft. Key behaviours:
- Results cached in-memory (same question never asked twice per run)
- Fails silently — always returns `""` on any error, never breaks the pipeline
- Uses `async with await NotebookLMClient.from_storage() as client:` — the `await` is required because `from_storage()` is a coroutine
- Storage state written to `~/.notebooklm/profiles/default/storage_state.json` (not `/tmp`)
- Parses `NOTEBOOKLM_STORAGE_STATE` with `json.JSONDecoder().raw_decode()` to tolerate trailing characters from GitHub Secrets

`scripts/export_notebook_knowledge.py` runs all 15 notebook queries inside a **single** `async with await NotebookLMClient.from_storage() as client:` block (one browser launch). Results unwrapped via `getattr(result, "answer", None) or str(result)`.

### Output files

| Path | Written by | Content |
|---|---|---|
| `outreach/leads-{city}-{date}.md` | `research_leads.py` | Raw leads grouped by niche with pitch angles and LinkedIn search links |
| `analysis/client-ranking-{date}.md` | `analyze_leads.py` | Scored + ranked leads with pricing, competitor comparison, and first-email hooks |
| `knowledge/nine-brand-knowledge.md` | `export_notebook_knowledge.py` | NINE brand knowledge base — 15 sections queried from NotebookLM |
| `audit/log.md` | `/audit` skill | Appended daily — scores, issues, and tomorrow's fixes across all 6 audit areas |
| `crm/week-{YYYY}-W{NN}.md` | `/crm` skill (via `/eod`) | Weekly lead tracker — all pipeline activity for the week |
| `crm/monthly-{YYYY-MM}.md` | `crm_merge.py` | Monthly CRM report — pipeline funnel, revenue forecast, niche + city breakdown |

## GitHub Actions

All workflows have `workflow_dispatch` enabled — trigger manually from the Actions tab without waiting for the schedule.

| Workflow | Schedule | Requires secret |
|---|---|---|
| `daily-leads.yml` | 7pm UTC daily | — |
| `analysis.yml` | 8pm UTC every 2 days | `NOTEBOOKLM_STORAGE_STATE` (optional) |
| `export-knowledge.yml` | Manual only | `NOTEBOOKLM_STORAGE_STATE` |
| `crm-monthly.yml` | 9am UTC on 1st | — |

`analysis.yml` installs `notebooklm-py[browser]` + Playwright before running. `export-knowledge.yml` checks out `claude/automated-outreach-system-FqALG` explicitly (scripts live there), runs the export, then `fetch + reset --hard + restore` to avoid push rejection from concurrent commits during the ~3-minute query window.

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

`crm_merge.py` deduplicates across week files by keeping the most advanced pipeline stage per business name. Pipeline stages in order: Found → Emailed → DM'd → Replied → Warm → Call Booked → Proposal Sent → Won → Lost.

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
- Full brand knowledge (voice, niche angles, objection handling, email guidelines) in `knowledge/nine-brand-knowledge.md`
