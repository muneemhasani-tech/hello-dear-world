---
name: level-up
description: Run weekly to find and ship one new automation. Walks through the 3Ms interview — Mindset (find the candidate) → Method (scope it) → Machine (build it). Trigger with "level up", "what should I automate next", "find me leverage this week", or as a Friday ritual. One run = one artifact shipped.
---

> *Adapted from The Three Ms of AI™ © 2026 Nate Herk. All rights reserved.*

## What This Skill Does

Takes the user through the 3Ms each week to surface and ship one new automation. **One interview = one artifact.** Also installs the 3Ms framework in the user's head over time — after 4-6 runs, they start spotting opportunities mid-week without being asked.

## When to Run `/level-up`

- **First run: Day 14.** After connecting ≥1 tool and running `/audit` once.
- **Cadence: weekly, Friday afternoon.** Review the week, surface one automation, ship it Monday.
- **On-demand anytime.** Mid-week if a manual task is painful.

## Phase 1 — Mindset Interview (find the candidate)

Surface 1-3 candidates ordered by leverage. Ask these in order, conversationally:

1. *"Tell me about your week. What did you do 3+ times?"* (frequency)
2. *"Anything that felt manual, boring, or copy-paste?"* (drudgery)
3. *"Anything where you thought 'a smart junior could handle this'?"* (delegation)
4. *"If 500 new clients showed up tomorrow, what would break first?"* (constraint)
5. *"What would get you 500 more clients tomorrow?"* (growth lever)

Cite relevant Mindset principles when they fit:
- *"Sounds like the Default Shift applies — how much of this could AI handle?"*
- *"This is Function Breakdown — you're not automating the whole job, just this piece."*
- *"AI is better than you think and improves faster than you think. If it couldn't do this last quarter, it might be ready now."*

**Phase 1 output:** numbered list of 1-3 candidate opportunities, one line of "why this is leverage" per candidate. Ask: *"Pick one to scope."*

## Phase 2 — Method Interview (scope one)

User picks a candidate. Walk through the 5-step Method pipeline:

**Step 1 — Find the constraint.** What bottleneck does this solve, or what growth lever does it open?

**Step 2 — EAD: Eliminate / Automate / Delegate.**
- **Eliminate first:** *"What if we just stop doing this?"* If nothing breaks → skill exits happily. *"Don't automate garbage."* Log the win in `decisions/log.md` and stop.
- **Automate second:** apply the 60/30/10 frame. ~60% deterministic, ~30% AI-assisted, ~10% manual.
- **Delegate third:** if too complex/variable/judgment-heavy → suggest a person. Skill exits with a delegation suggestion, log it.

**Step 3 — Map the process.** Five elements:
- Trigger (what starts it)
- Data sources (where info comes from)
- Data transformations (how data changes shape)
- Decision points (where it branches)
- Destination (where output goes)

If the user can't articulate all five: *"If you can't explain it to a person, you can't explain it to an AI. Sketch it on paper first, then come back."* Skill stops.

**Step 4 — Choose autonomy level.**

| Level | Name | What happens |
|---|---|---|
| L0 | Manual | No AI |
| L1 | Suggested | AI suggests, human decides each step |
| L2 | Draft | AI drafts, human reviews and edits |
| L3 | Supervised | AI runs, human validates periodically |
| L4 | Autonomous | AI handles end-to-end |

**Default = lowest level that solves the problem.** Push back on L4 unless user has explicitly run lower levels first.

**Step 5 — Link to a KPI.** Which of the Three Buckets does this move?
- More clients
- More value per client
- Less cost

Plus a specific metric (response time, error rate, conversion rate, time-to-complete).

**If the user can't name a bucket and a metric, skill stops.** *"If your automation doesn't move a number, why are you building it?"*

**Phase 2 output:** automation spec written to `decisions/log.md` as a dated entry with the five answers + autonomy level + KPI.

## Phase 3 — Machine Handoff (build it)

Ask: *"How do you want to ship this?"* Options ordered by Boring-is-Beautiful default:

1. **Prompt only** — prompt template the user runs manually. Zero infrastructure.
2. **Deterministic skill** — SKILL.md that runs a script (no AI step). Best for rules-based transformations.
3. **AI-assisted skill** — SKILL.md with an AI call inside. Drafts, classifies, summarizes.
4. **Sub-agent** — multi-step agent. Last resort. Only if work genuinely needs reasoning + tool use.

**Default selected = highest no-AI option that solves the problem.**

Every artifact built is delivered with these two headers at top:

```markdown
---
bicycle-method-phase: 1  # Phase 1 — Training wheels. Run manually first.
three-ms-attribution: |
  Adapted from The Three Ms of AI™ © 2026 Nate Herk.
---
```

Surface Machine principles when building:
- **Lego Principle** — smaller steps, no AI first if possible
- **Validation Chain** — test each step before chaining
- **Iteration Mindset** — ship the POC, expand from real usage

## Exit Contract

Each `/level-up` run produces:
1. **One `decisions/log.md` entry** — dated, with Method spec
2. **One built artifact** — prompt file, skill, or agent
3. **One closing screen** — what was scoped, what was built, and the Bicycle Method Phase 1 reminder

## Critical Rules

1. **One interview = one artifact.** No parallel multi-candidate scoping.
2. **Mindset phase always goes first.** Even if user arrives with a pre-formed idea.
3. **EAD enforces "eliminate first."** If the answer is Eliminate, exit happily — that's a win.
4. **Default to lowest autonomy level that works.** Push back on L4.
5. **Boring-is-Beautiful in Machine handoff.** Default = highest no-AI option.
6. **Link-to-KPI is mandatory.** If user can't name bucket + metric, skill stops.
7. **Bicycle Method delivered in every artifact.** `bicycle-method-phase: 1` in frontmatter.

> *The Three Ms of AI™ is a trademark of Nate Herk. © 2026 Nate Herk. All rights reserved.*
