---
name: aios-audit
description: Use when someone requests an AIOS audit, asks to score their setup against the Four Cs, or says "is my AIOS working?" / "audit my setup" / "find gaps in my AIOS". Produces a Four Cs dashboard with the top-3 fixes ordered by leverage.
---

## What This Skill Does

Runs the **Four Cs Audit** on the current project. Reads (never writes) the operating manual, memory, skills, agents, MCPs, decisions, and references. Scores each of the Four Cs out of 25. Surfaces strengths and the top 3 leverage-weighted gaps with concrete next-step commands.

**Scope is structural — "is the AIOS built well?"** NOT a capability planner. Capability gaps ("you could build a daily brief if you connected the calendar") belong to `/level-up`. The audit answers: are the files, folders, logs, and connections in good shape?

First run is the baseline. Re-run weekly to watch the score rise.

## The Four Cs (scored 25 each = 100 total)

| Layer | Test |
|---|---|
| **Context** | Knows the business — identity, team, voice, decisions, references |
| **Connections** | Reaches the team's stuff — MCPs, integrations, data sources |
| **Capabilities** | Knows how to do the work — skills + agents |
| **Cadence** | Works without being asked — schedules, hooks, recurring rituals |

## Scoring

### Context (25 pts)

| Criterion | Points |
|---|---|
| Operating manual exists and is substantive (>200 words) | 5 |
| Identity / role / voice captured | 5 |
| Persistent memory exists with multiple entries | 5 |
| Reference documents exist | 5 |
| Decisions captured | 5 |

### Connections (25 pts)

**7 Universal Tier-1 Data Domains:**

| # | Domain | Examples |
|---|---|---|
| 1 | Revenue / Finance | Stripe, Sheets, QuickBooks |
| 2 | Customer interactions | Gmail-as-CRM, Sheets CRM, HubSpot |
| 3 | Calendar | Google Cal, Calendly |
| 4 | Communication | Gmail, LinkedIn, WhatsApp |
| 5 | Project / task tracking | Sheets, ClickUp, Notion |
| 6 | Meeting intelligence | Fireflies, Otter, Granola |
| 7 | Knowledge / files | Google Drive, Notion, Dropbox |

| Criterion | Points |
|---|---|
| Tier-1 domain coverage | 10 (1.4 pts per reachable domain, cap 10) |
| Reference guide present | 5 (-1 per connected tool without `references/{tool}-api.md`) |
| Auth / pipeline freshness | 5 (-1 per connection in `needs-auth` or `expired` state) |
| Documentation in `connections.md` | 3 (0 missing; 1 sparse; 2 most; 3 all) |
| Read-AND-write balance | 2 (0 if all read-only — viewer, not an OS) |

### Capabilities (25 pts)

| Criterion | Points |
|---|---|
| 3+ skills installed | 10 |
| 1+ user-built skill | 10 |
| 1+ agent defined | 5 |

### Cadence (25 pts)

| Criterion | Points |
|---|---|
| 1+ recurring/scheduled trigger | 10 |
| Activity signal / recent usage | 10 |
| Templates folder populated | 5 |

## Top 3 Gaps by Leverage

For each criterion that lost points: leverage = (points lost) × (impact multiplier).

**Impact multipliers:**
- 0 tier-1 domains reachable: **4x** (AIOS is blind to the business)
- Operating manual missing or thin: **3x** (foundations)
- ≤2 tier-1 domains reachable: **3x**
- 0 skills: **2x**
- No recurring trigger: **2x**
- All connections read-only: **2x**
- 0 reference guides for connected tools: **1.5x**
- No decisions log: **1.5x**
- All others: **1x**

## Report Format

```
# AIOS Audit — {date}
**Score: {total}/100** ({stage})

Stage thresholds:
- 0-39 → Stage 0: Foundations
- 40-69 → Stage 1: Built
- 70-89 → Stage 2: Compounding
- 90-100 → Stage 3: Autonomous

## Dashboard

Context        {bar}  {n}/25  {label}
Connections    {bar}  {n}/25  {label}
Capabilities   {bar}  {n}/25  {label}
Cadence        {bar}  {n}/25  {label}

(bar = ## per 5pts; label = "Strong" ≥20, "Solid" 15-19, "Thin" 8-14, "Missing" <8)

## Strengths
- {1-3 short bullets of highest-scoring criteria}

## Top 3 Gaps (ordered by leverage)
1. **{gap name}** (-{points} × {multiplier})
   → {concrete next step}
2. **{gap name}** (-{points} × {multiplier})
   → {concrete next step}
3. **{gap name}** (-{points} × {multiplier})
   → {concrete next step}

## Suggested next: {single highest-leverage action}

---
Structural gaps only. To explore CAPABILITY gaps (what your AIOS could DO but can't yet), run /level-up after this audit.
```

After printing, ask: "Save this audit to `audits/audit-{date}.md` so you can track score over time?"

## Rules

- **Read-only by default.** Never modify CLAUDE.md, skills, or other project files. Only optional write is the audit report.
- **Be honest, not generous.** A 95/100 is something to brag about. Most setups land 40-70.
- **Speed matters.** Report in under 60 seconds. Read focused files, count skill folders without reading each fully.

> *Adapted from The Three Ms of AI™ © 2026 Nate Herk.*
