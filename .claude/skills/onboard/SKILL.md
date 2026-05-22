---
name: onboard
description: Run on Day 1 of an AIOS install, when someone says "set me up", "onboard me", "let's start", or "fill my AIOS", or just cloned the kit. Combined assistant — runs the 7-question interview AND builds the Day 1 file set at the end. Idempotent — re-run anytime after editing aios-questionnaire.md.
---

## What This Skill Does

Single combined assistant. Reads or writes `aios-questionnaire.md`, runs the 7-question interview if the file isn't filled, then builds the Day 1 file set inline at the end. One flow.

**The "wow" moment:** at the end, suggest the closing prompt *"Try this — ask me: what should I focus on this week?"* The user runs it once. That's the wow. No separate `/today` skill to save — the prompt itself plants the Mindset frame (Default Shift) for them to internalize.

## Execution

### Step 1: Read the questionnaire

Read `aios-questionnaire.md`. Check which Q1-Q7 sections have content vs. `[Your answer here]` placeholders.

- **All filled** → skip Step 2, jump to Step 3 (build).
- **Some filled** → ask: "I see Q1, Q3, Q4 are answered. Want to fill the rest now, or build with what's here?" Their call.
- **None filled (fresh clone)** → run Step 2 conversationally.

### Step 2: The interview (7 questions, hard cap)

Ask one at a time. Write each answer into `aios-questionnaire.md` as you go.

**Q1 — Who are you, what do you sell, and who do you sell it to?**
Identity, offer, ICP. One paragraph each is fine.

**Q2 — Paste 1-2 things you've written recently. Don't edit them.**
*This is the only question with a hard rule.* Voice samples MUST be pasted, not written mid-conversation. If the user starts typing fresh prose, reject:

> *"Stop — paste it raw. If you write it here while we're talking, the sample is already shaped by our conversation. Open your last email or LinkedIn post in another tab and paste the unedited text. This is the one rule I can't bend."*

Ask for two samples. An email, a post. Or two of either.

**Q3 — What are your 2-3 biggest priorities for the next 90 days?**
Quarterly priorities. Push back if they say "grow my business" — make them name a number, a deadline, or a deliverable.

**Q4 — Where does revenue actually land, and where is it tracked?**
Multiple answers fine. Maps to Domain 1 (Revenue/Finance).

**Q5 — Where do you talk to clients, your team, and the outside world day-to-day?**
Email (Gmail/Outlook), WhatsApp, LinkedIn DMs, Slack. Maps to Domains 2 + 4.

**Q6 — Where do meeting recordings, notes, and important docs live?**
Maps to Domains 6 + 7.

**Q7 — What is the ONE task eating your week, and where do you track work currently?**
Captures top_pain (used by `/level-up` Day 14) + Domain 5 (tasks).

Domain 3 (Calendar) is inferred from Q5: Gmail → Google Cal. Confirm in Step 3.

### Step 3: Build the Day 1 file set

Once questionnaire is complete, generate these files (or update them on re-run).

1. **`context/about-me.md`** — from Q1 (identity, role) + Q7 (top_pain). Short paragraph each.
2. **`context/about-business.md`** — from Q1 (offer, ICP) + Q4 (revenue model). One paragraph.
3. **`context/priorities.md`** — from Q3. Numbered list, one line per priority.
4. **`references/voice.md`** — from Q2. Paste samples verbatim with a short header explaining their use.
5. **`connections.md`** — populate the 7-row table from Q4-Q7 answers. Each row gets `mechanism: not connected`, `auth: —`, `last verified: —`. User connects Day 2.
6. **`CLAUDE.md`** — fill all `{{...}}` placeholders. Substitute team name, declared priority, voice log summary, and a short connections summary.

### Step 4: Closing screen

Print one screen. Three lines max:

```
✓ Day 1 complete. Your AIOS knows who NINE is, what you sell, what matters this quarter, and how you sound.

Today: ask me — "what should we focus on this week?"
Tomorrow: pick one tool from connections.md and connect it (Apps Script, n8n, or a small API script + save references/{tool}-api.md).
Day 7: run /aios-audit to see your score.
```

When the user runs the closing prompt ("what should we focus on this week?"), respond using only the new context files. Hit:
- 3-bullet priority list, in their Q2 voice register
- Each bullet tied to a declared 90-day priority from Q3
- Final line: *"If I had to pick one thing for Monday, it's [X], because [reason from priorities]. Want me to draft the first outreach? And — where could the Default Shift apply here? How much of this could AI handle?"*

## Critical Rules

1. **7-question cap is non-negotiable.** Don't add Q8 in conversation.
2. **Voice paste cannot be skipped.** If user types samples mid-chat, reject and ask them to paste from real writing.
3. **Build in one shot.** After Step 2, write Step 3 files in one batch.
4. **Idempotent.** Re-running with an edited questionnaire refreshes context files; backs up originals to `archive/questionnaire-{ts}/`.
5. **Closing screen is three lines.** Not a menu.
6. **No extra skills generated.** Don't build `/today`, `/draft`, `/connect`, etc. Kit ships 3 skills; user creates more via `/level-up`.

> *Adapted from The Three Ms of AI™ © 2026 Nate Herk.*
