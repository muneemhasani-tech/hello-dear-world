---
name: dm
description: Draft LinkedIn connection notes and follow-up DMs for NINE decision makers. Trigger with "/dm", "draft LinkedIn messages", "write DMs", or "LinkedIn outreach".
disable-model-invocation: true
---

## What This Skill Does

Reads the "LinkedIn DM Targets" section from today's leads file and drafts two things per decision maker:
1. A connection request note (≤300 chars)
2. A follow-up DM for after they accept (sent 24–48h later)

## Context to load

Read:
- `outreach/leads-{city}-{date}.md` — "LinkedIn DM Targets" section (most recent file)
- `knowledge/nine-brand-knowledge.md` — brand voice and DM guidelines (if exists)

## Target profile

Decision makers: Owners, Founders, CMOs at companies with 11–1,000 employees. Avoid HR, coordinators, assistants.

## Connection note rules (≤300 characters)

- Reference something specific: their niche, a product, their content
- Mention NINE's focus (motion graphics / reels / creator content) naturally
- No hard pitch in the connection note — just relevance
- End with a light hook or question

Example format:
> "Saw [Company]'s [product/post] — love what you're doing in [niche]. We help brands like yours turn that into scroll-stopping reels. Would love to connect."

## Follow-up DM rules

- Send only after they accept (24–48h wait)
- Open with a compliment or observation specific to their business
- One sentence on what NINE does, one result or case study reference
- Soft CTA: "Would a 15-min chat make sense?" or "Worth exploring?"
- Max 80 words

## Output format

For each decision maker:

```
### {Name} — {Title} @ {Company}
🔗 {LinkedIn URL}

**Connection note:**
{note ≤300 chars}

**Follow-up DM (send after accept):**
{DM ≤80 words}
```

After all DMs: "Send connection notes today. Set a reminder to send follow-up DMs 24–48h after each accepts. Run /crm to log DMs sent."
