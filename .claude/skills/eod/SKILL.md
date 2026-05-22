---
name: eod
description: End-of-day review for NINE outreach pipeline. Scores day against targets, flags follow-ups, confirms tomorrow's city. Auto-triggers /crm and /audit. Use when someone says "/eod", "end of day", "wrap up", or "day review".
disable-model-invocation: true
---

## What This Skill Does

Closes the outreach day. Reviews what happened, scores against daily targets, flags anything needing follow-up tomorrow, confirms tomorrow's city, then triggers /crm and /audit.

## Daily targets

| Metric | Target |
|---|---|
| Businesses found | 30 |
| Emails sent | 20 |
| LinkedIn connections sent | 20–40 |
| Chats started | 5–10 |
| Serious leads identified | 2–3 |

## Execution

### Step 1 — Day review questions

Ask these conversationally (can be answered in one message):

1. How many businesses did you find / add today?
2. How many cold emails did you send?
3. How many LinkedIn connection requests did you send?
4. Any replies or conversations started?
5. Any serious leads (Warm or above)?
6. Anything to follow up on tomorrow?

### Step 2 — Score vs targets

Print a simple scorecard:

```
## Day Scorecard — {date}

| Metric | Target | Actual | Status |
|---|---|---|---|
| Businesses found | 30 | N | ✓/✗ |
| Emails sent | 20 | N | ✓/✗ |
| LinkedIn connections | 20–40 | N | ✓/✗ |
| Chats started | 5–10 | N | ✓/✗ |
| Serious leads | 2–3 | N | ✓/✗ |
```

### Step 3 — Follow-up flags

List anything that needs action tomorrow:
- Leads who opened but didn't reply (if tracked)
- Connections who accepted but haven't received follow-up DM
- Warm leads needing a nudge
- Any promised deliverables (proposals, samples)

### Step 4 — Tomorrow's city

Calculate tomorrow's city: `(today_ordinal + 1) % 50` from the CITIES list in `research_leads.py`. Print: "Tomorrow's city: {City}"

### Step 5 — Auto-trigger

Print:
```
---
Running /crm to log today's activity...
```
Then execute the /crm skill to update the weekly file with today's leads and stages.

Then print:
```
Running /audit to score the day...
```
Then execute the /audit skill.

## Closing line

"Day wrapped. {N} leads in pipeline, {N} hot. Rest up — {Tomorrow's city} tomorrow."
