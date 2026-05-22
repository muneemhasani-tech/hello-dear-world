---
name: morning
description: Daily morning briefing for NINE outreach pipeline. Use when someone says "morning", "good morning", "start my day", "what's today", or "/morning". Shows today's city, top 3 leads, and LinkedIn DMs ready to send.
disable-model-invocation: true
---

## What This Skill Does

Opens the day for the NINE outreach pipeline. Reads today's leads file, surfaces the top 3 highest-potential businesses, and lists LinkedIn DM targets ready to contact.

## Execution

### Step 1 — Identify today's city

Today's date is available via the system. City is selected by `date.toordinal() % 50` across the 50-city rotation in `research_leads.py`. Read the most recent `outreach/leads-{city}-{date}.md` file — today's date first, then the most recent if today's doesn't exist yet.

If no leads file exists for today: "No leads file yet for today — run `python scripts/research_leads.py` or trigger the daily-leads workflow."

### Step 2 — Top 3 leads

From the leads file, pick the 3 businesses with the strongest pitch angle. Prefer:
- Businesses with a website listed (can be analysed)
- Niches with highest NINE fit: restaurants → health/wellness → events → FMCG
- Any business flagged with a clear web issue

For each of the 3, print one line:
```
1. **Business Name** (niche) — web.site — pitch angle in one sentence
```

### Step 3 — LinkedIn DM targets

Check the "LinkedIn DM Targets" section at the bottom of today's leads file. List each decision maker with their name, title, and company. If none exist yet: "No DM targets enriched yet — add decision makers to the LinkedIn DM Targets section, then run /dm."

### Step 4 — Day summary line

Print one line:
```
Today: {City} | {N} businesses found | {N} DM targets ready | Run /outreach to draft emails
```

## Output Format

```
# Good morning — {Day}, {Date}

**Today's city:** {City}

## Top 3 Leads
1. **Name** (niche) — website — pitch angle
2. **Name** (niche) — website — pitch angle
3. **Name** (niche) — website — pitch angle

## LinkedIn DM Targets
- **Name**, Title @ Company — [LinkedIn profile]

Today: {City} | {N} businesses | {N} DM targets | Run /outreach to draft emails
```
