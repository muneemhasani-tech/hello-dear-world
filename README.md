# NINE Automated Outreach Pipeline

An AI-powered B2B lead research and outreach system for creative agencies. Runs entirely on GitHub Actions — no server, no database, no paid scraping API. Outputs structured markdown files committed back to the repo.

Built for **NINE**, a motion graphics and branding agency targeting restaurants, health/wellness, FMCG, and events businesses across Tier 2 US, UK, and Australian cities.

---

## What it does

```
Daily (7pm UTC)               Every 2 days (8pm UTC)        1st of month (9am UTC)
research_leads.py        →    analyze_leads.py          →   crm_merge.py
  picks a city by date          reads each lead's sitemap      reads all week files
  scrapes DuckDuckGo            scores web gap (0–100)         deduplicates leads
  finds 8 leads/niche           maps to pricing tier           writes monthly report
  writes outreach/             writes analysis/
    leads-{city}-{date}.md       client-ranking-{date}.md
```

- **No API keys required** for the core pipeline (`research_leads.py`, `analyze_leads.py`, `crm_merge.py` use Python stdlib only)
- **Optional NotebookLM integration** adds brand-voice email hooks to the analysis step
- **17 Claude Code skills** included for the daily outreach workflow (`/morning`, `/outreach`, `/dm`, `/reply`, `/post`, `/crm`, `/eod`, `/audit` and more)

---

## Quick start

### 1. Clone and configure

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

Edit `scripts/research_leads.py`:
- **`CITIES`** (line 16) — replace or extend with your target cities
- **`NICHES`** (line ~70) — replace with your target niches

Edit `CLAUDE.md`:
- Replace all references to "NINE" with your agency name
- Update the agency context section (brand voice, offer, ICP)

### 2. Run locally

```bash
# Research leads for today's city (no dependencies)
python scripts/research_leads.py

# Analyse all leads and produce a ranked report (no dependencies)
python scripts/analyze_leads.py

# Generate this month's CRM report
python scripts/crm_merge.py          # current month
python scripts/crm_merge.py 2026 5   # specific month
```

Output files are printed to stdout. Progress and errors go to stderr.

### 3. Set up GitHub Actions

Push to your repo. The workflows in `.github/workflows/` run automatically:

| Workflow | Schedule | What it does |
|---|---|---|
| `daily-leads.yml` | 7pm UTC daily | Runs `research_leads.py`, commits output |
| `analysis.yml` | 8pm UTC every 2 days | Runs `analyze_leads.py`, commits output |
| `crm-monthly.yml` | 9am UTC on 1st | Runs `crm_merge.py`, commits output |
| `export-knowledge.yml` | Manual only | Exports NotebookLM knowledge base |

All workflows have `workflow_dispatch` — trigger manually from the Actions tab any time.

No secrets required for the core pipeline. See [NotebookLM setup](#notebooklm-optional) for the optional AI step.

### 4. Use Claude Code skills (optional)

If you use [Claude Code](https://claude.ai/code), the skills in `.claude/skills/` are automatically available in every session:

```
/morning    — today's city, top 3 leads, LinkedIn DMs ready
/outreach   — drafts 5 cold emails from today's leads file
/dm         — drafts LinkedIn connection notes + follow-up DMs
/reply      — classifies a lead's reply and drafts the next message
/post       — generates AI content prompt for a warm lead
/crm        — logs leads, shows pipeline summary
/eod        — end-of-day review, auto-triggers /crm and /audit
/audit      — scores the day across 6 areas, appends to audit/log.md
```

---

## Customising for your agency

### Cities

`research_leads.py` picks a city daily by `date.toordinal() % len(CITIES)`. Edit the `CITIES` list to target your markets. The current list covers 50 Tier 2 cities across the US, UK, and Australia.

### Niches

The `NICHES` list in `research_leads.py` controls what's searched in each city. Default: `restaurants`, `health_wellness`, `fmcg`, `events`. Change these to match your agency's target verticals.

### Agency context (outreach copy)

The skills use brand context from two sources:
1. **`CLAUDE.md`** — the "Agency context" section at the bottom
2. **`knowledge/nine-brand-knowledge.md`** — exported from NotebookLM (optional, see below)

Update the agency context section in `CLAUDE.md` with your:
- Core offer / entry product
- Pitch angle
- Target decision makers
- Brand voice notes

### Scoring and pricing tiers

`analyze_leads.py` scores each lead 0–100 and maps to a pricing tier:

| Score | Tier | Price range |
|---|---|---|
| 80–100 | Full Rebuild | $8k–$18k |
| 60–79 | Growth | $4k–$8k |
| 40–59 | Upgrade | $2k–$4k |
| 20–39 | Quick-Win | $1k–$2k |
| 0–19 | SEO/Maintenance | $300–$800/mo |

Adjust these thresholds and prices in `analyze_leads.py` to match your service menu.

---

## NotebookLM (optional)

The analysis step can pull brand-voice email hooks from a Google NotebookLM notebook before drafting each lead's first email. This is entirely optional — the pipeline degrades gracefully without it.

### Setup

1. Create a NotebookLM notebook at [notebooklm.google.com](https://notebooklm.google.com) and load it with your agency's brand docs, case studies, and email examples.

2. Get your notebook ID from the URL: `notebooklm.google.com/notebooklm#notebook/{NOTEBOOK_ID}`

3. Set the `NOTEBOOKLM_NOTEBOOK_ID` environment variable:
   - **Locally:** add to your `.env` file (see `.env.example`)
   - **GitHub Actions:** add as a repository secret named `NOTEBOOKLM_NOTEBOOK_ID`

4. Capture your browser storage state:
   ```bash
   pip install "notebooklm-py[browser]" && playwright install chromium
   # Log into NotebookLM in a browser, then export storage state JSON
   ```
   Set `NOTEBOOKLM_STORAGE_STATE` to the full JSON string (as a secret in GitHub Actions).

5. Install dependencies for local use:
   ```bash
   pip install "notebooklm-py[browser]"
   playwright install chromium
   ```

If `NOTEBOOKLM_STORAGE_STATE` is not set, `analyze_leads.py` skips the NotebookLM step and uses data-driven fallback hooks instead. The pipeline always produces output.

---

## File structure

```
.
├── .claude/
│   └── skills/              # Claude Code skills (auto-loaded in web sessions)
│       ├── audit/
│       ├── morning/
│       ├── outreach/
│       └── ...              # 17 skills total
├── .github/
│   └── workflows/           # GitHub Actions (runs the pipeline on schedule)
├── analysis/
│   └── client-ranking-{date}.md   # Scored + ranked leads with email hooks
├── audit/
│   └── log.md               # Daily audit scores (appended by /audit)
├── crm/
│   └── week-{YYYY}-W{NN}.md       # Weekly lead tracker (created by /eod)
│   └── monthly-{YYYY-MM}.md       # Monthly CRM report (created by crm_merge.py)
├── knowledge/
│   └── nine-brand-knowledge.md    # Brand knowledge base (from NotebookLM)
├── outreach/
│   └── leads-{city}-{date}.md     # Raw leads by city and date
├── scripts/
│   ├── research_leads.py          # Daily lead scraper
│   ├── analyze_leads.py           # Sitemap analyser + scorer
│   ├── crm_merge.py               # Monthly CRM report generator
│   ├── notebooklm_context.py      # NotebookLM query utility (used by analyze_leads)
│   └── export_notebook_knowledge.py  # One-time knowledge base exporter
├── .env.example             # Environment variable reference
├── CLAUDE.md                # Claude Code project instructions
└── README.md
```

---

## Daily workflow

```
/morning → /outreach → /dm → /reply [paste] → /post [company] → /eod → /crm (auto) → /audit (auto)
```

**Daily targets:** 30 businesses found · 20 emails sent · 20–40 LinkedIn connections · 5–10 chats started · 2–3 serious leads

**Pipeline stages:** Found → Emailed → DM'd → Replied → Warm → Call Booked → Proposal Sent → Won → Lost

---

## Requirements

- Python 3.12+ (core pipeline — stdlib only, no pip install needed)
- `notebooklm-py[browser]` + Playwright (optional, for NotebookLM integration only)
- GitHub repository with Actions enabled (for scheduled runs)
- [Claude Code](https://claude.ai/code) (optional, for the `/skill` workflow)

---

## Adapting to another agency

1. Fork or clone the repo
2. Edit `CITIES` and `NICHES` in `research_leads.py`
3. Replace agency context in `CLAUDE.md` (offer, pitch angle, voice, ICP)
4. Update pricing tiers in `analyze_leads.py`
5. Optional: replace `knowledge/nine-brand-knowledge.md` with your own knowledge base
6. Push — GitHub Actions handles the rest

The scripts contain no references to NINE's brand in the logic itself. All agency-specific content lives in `CLAUDE.md`, `knowledge/`, and the skill files.
