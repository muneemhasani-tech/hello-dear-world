---
name: audit
description: Score NINE's outreach day across 6 areas, log mistakes, write tomorrow's fix list. Appends to audit/log.md. Trigger with "/audit", "score my day", "audit today", or auto-triggered by /eod.
disable-model-invocation: true
---

## What This Skill Does

Scores the outreach day across 6 areas (1–5 each). Surfaces what went wrong, writes 3 concrete fixes for tomorrow, and appends the result to `audit/log.md`.

## Scoring areas (1–5 each, 30 total)

| Area | What to score |
|---|---|
| **Lead quality** | Were the businesses found genuinely good fits for NINE? (right niche, right size, clear content gap) |
| **Email personalisation** | Were emails specific to each business, or generic? |
| **LinkedIn connection relevance** | Were connection requests sent to the right decision makers? |
| **Reply timing** | Were replies answered within the session / same day? |
| **CRM accuracy** | Was the CRM updated with today's activity? Are stages correct? |
| **Next-day prep** | Is tomorrow's follow-up list clear? Tomorrow's city confirmed? |

## Scoring guide

- **5** — Excellent, no gaps
- **4** — Good, minor gap
- **3** — Acceptable, one clear miss
- **2** — Below target, multiple misses
- **1** — Did not happen or significantly off

## Execution

### Step 1 — Ask for context (if not already from /eod)

"Quick audit — score yourself 1–5 on each area, or tell me what happened and I'll score it."

If coming from /eod, use the data already collected in that session.

### Step 2 — Print scorecard

```
## Audit — {date}

| Area | Score | Note |
|---|---|---|
| Lead quality | N/5 | one line |
| Email personalisation | N/5 | one line |
| LinkedIn relevance | N/5 | one line |
| Reply timing | N/5 | one line |
| CRM accuracy | N/5 | one line |
| Next-day prep | N/5 | one line |

**Total: N/30**
```

### Step 3 — Mistakes

List 1–3 specific things that went wrong today. Be honest, not generous.

### Step 4 — Tomorrow's fixes

Write 3 concrete, actionable fixes for tomorrow. Not vague ("do better") — specific ("send follow-up DM to the 3 connections who accepted but haven't heard from you").

### Step 5 — Append to audit/log.md

Append the full scorecard + mistakes + fixes to `audit/log.md` with a timestamp header:

```markdown
## {date} — Total: N/30

| Area | Score |
|---|---|
...

**Mistakes:** ...
**Tomorrow's fixes:**
1. ...
2. ...
3. ...
```

Create `audit/log.md` if it doesn't exist.
