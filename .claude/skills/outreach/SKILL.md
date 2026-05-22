---
name: outreach
description: Draft 5 personalised cold emails for NINE from today's leads file. Trigger with "/outreach", "draft emails", "write cold emails", or "email today's leads".
disable-model-invocation: true
argument-hint: [city-date]
---

## What This Skill Does

Reads today's leads file and drafts 5 personalised cold emails using NINE's brand voice and the Content Sprint offer. Emails are ready to copy-paste or lightly edit before sending.

## Context to load first

Before drafting, read:
- `outreach/leads-{city}-{date}.md` — today's leads (most recent file if date not specified)
- `knowledge/nine-brand-knowledge.md` — brand voice, niche angles, objection handling, email guidelines

If `nine-brand-knowledge.md` doesn't exist, proceed with brand rules embedded below.

## NINE Brand Rules (embedded fallback)

- **Lead with proof** — reels, case studies, results. Never mention Bangladesh unprompted.
- **First offer** — always the Content Sprint: 2-week trial — brand spine + 15 reels + creator collab
- **Pitch angle** — businesses with stunning products but flat socials or fragmented UGC
- **Decision makers** — Owners, Founders, CMOs at 11–1000 employee companies
- **Tone** — direct, specific, no fluff. Reference something real about their business.
- **Subject lines** — specific, not clickbait. Name the business or niche.
- **No location mention** unless they bring it up.

## Email structure

Each email:
1. **Subject line** — specific hook referencing their business/niche
2. **Opening** — one sentence about something real (their product, their social presence, a recent post)
3. **Problem** — one sentence on the gap (flat reels, inconsistent UGC, no brand video)
4. **Offer** — Content Sprint pitch, one sentence
5. **CTA** — single low-friction ask (15-min call, or "worth a chat?")
6. **Sign-off** — brief, no fluff

Max 120 words per email body.

## Execution

1. Pick the 5 highest-potential leads from today's file (prioritise those with websites and clear web issues)
2. For each, draft one email using the structure above
3. Print all 5 sequentially, labelled 1–5
4. After all 5: "Copy any of these to your email client. Run /crm to log which ones you send."

## Niche angle shortcuts

- **Restaurants** — food reels, chef behind-the-scenes, dish launches, event nights
- **Health/wellness** — transformation content, expert credibility, community UGC
- **FMCG** — product hero shots, lifestyle reels, influencer seeding
- **Events** — hype content, recap reels, speaker/performer spotlights
