---
name: post
description: Generate a platform-specific AI content prompt, reference image brief, and company data card for a lead who replied. Trigger with "/post [company name]" or "create a post for [company]".
disable-model-invocation: true
argument-hint: [company-name]
---

## What This Skill Does

For a lead who has replied and is warming up, generates:
1. A company data card (who they are, their niche, their content gap)
2. A platform-specific AI generation prompt
3. A reference image/video brief

This gives NINE a ready-to-send creative proposal or a spec to hand to a creator.

## Step 1 — Identify company

If company name is provided as argument, use it. Otherwise ask: "Which company are we creating for?"

Look up the company in:
- Today's leads file (`outreach/leads-*.md`)
- Any analysis file (`analysis/client-ranking-*.md`)

Extract: business name, website, niche, web issue, pitch angle.

## Step 2 — Ask platform

Ask (don't assume):

> "Which platform are we generating for?"
> 1. Higgsfield (video — cinematic reels)
> 2. Midjourney (image — product/lifestyle)
> 3. Runway (video — motion, transitions)
> 4. Adobe Firefly (image — brand-safe, commercial)

Wait for answer before proceeding.

## Step 3 — Generate output

### Company data card
```
**Company:** {name}
**Website:** {url}
**Niche:** {niche}
**Content gap:** {web issue / flat socials / no reels}
**Pitch angle:** {one sentence}
**Decision maker:** {name + title if known}
```

### Platform-specific prompt

**Higgsfield / Runway (video):**
> Cinematic reel for {niche} brand. Scene: {product/dish/service in action}. Lighting: {warm/natural/dramatic}. Motion: {slow push in / tracking shot / handheld}. Mood: {aspirational/energetic/premium}. No text overlay. 9:16 vertical format. Duration: 15s.

**Midjourney / Firefly (image):**
> {Product/service} hero shot, {niche} brand aesthetic, {lighting style}, shot on {camera feel}, {colour palette}, ultra-detailed, commercial photography, 4:5 ratio

Adapt specifically to their niche and product using context from the leads file.

### Reference image brief
```
**Style reference:** {describe 2-3 comparable brands or visual references}
**Mood:** {one word}
**Colours:** {brand colours if known, else niche-appropriate palette}
**Must include:** {product / logo space / lifestyle element}
**Must avoid:** {stock photo feel / text-heavy / generic}
```

## Step 4 — Closing line

"Send the data card to the lead as a preview of what NINE would create for them. Use the prompt in {platform} to generate a sample. Run /crm to log this as a Warm touchpoint."
