---
name: crm
description: Log or update leads in the current week's CRM file, or show pipeline summary. Trigger with "/crm", "log this lead", "update CRM", "pipeline summary", or auto-triggered by /eod.
disable-model-invocation: true
---

## What This Skill Does

Maintains `crm/week-{YYYY}-W{NN}.md` — the weekly lead tracker. Logs new leads, updates pipeline stages, and shows the current pipeline summary on demand.

## CRM file location

`crm/week-{YYYY}-W{NN}.md` where YYYY is the current year and NN is the ISO week number (zero-padded). Example: `crm/week-2026-W21.md`

Create the file if it doesn't exist for the current week.

## Pipeline stages (in order)

Found → Emailed → DM'd → Replied → Warm → Call Booked → Proposal Sent → Won → Lost

## CRM file format

```markdown
# CRM — Week {YYYY}-W{NN}

| Business | Website | Niche | Stage | Last Action | Next Action | Value |
|---|---|---|---|---|---|---|
| Name | url | niche | Stage | What happened | What's next | $X |
```

## Execution

### Called standalone (no arguments)

Show the current week's pipeline summary:

```
# Pipeline — Week {YYYY}-W{NN}

| Stage | Count | Value |
|---|---|---|
| Found | N | — |
| Emailed | N | — |
| DM'd | N | — |
| Replied | N | — |
| Warm | N | $Xk |
| Call Booked | N | $Xk |
| Proposal Sent | N | $Xk |
| Won | N | $Xk |
| Lost | N | — |

**Total pipeline value:** $Xk
**Hot leads (Warm+):** N
```

### Called with lead data (from /eod, /reply, /outreach)

Ask for any missing fields:
- Business name
- Stage
- Last action (one line: "Sent cold email", "LinkedIn DM'd", "They replied — interested")
- Next action (one line: "Follow up Thursday", "Send proposal", "Book call")
- Estimated value (use pricing tiers from analysis if known, else leave blank)

Then write or update the row in the weekly file.

**Stage precedence:** if a business already exists in the file, only update the stage if the new stage is more advanced. Never downgrade a stage.

## Pricing tier reference (from analysis pipeline)

- Full Rebuild: $8k–$18k
- Growth: $4k–$8k
- Upgrade: $2k–$4k
- Quick-Win: $1k–$2k
- SEO/Maintenance: $300–$800/mo
