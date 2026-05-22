---
name: agent-skills
description: Help writing SKILL.md files, encoding SOPs as skills, and setting skill triggers. Triggers on "how do I write a skill", "create a skill", "SKILL.md", "encode this as a skill", "make this a slash command", "skill triggers".
disable-model-invocation: false
---

## What This Skill Does

Guides writing SKILL.md files that encode SOPs, workflows, and knowledge as reusable Claude skills.

## SKILL.md structure

```yaml
---
name: skill-name                    # used as /skill-name trigger
description: When to use this.      # Claude reads this to decide when to auto-invoke
disable-model-invocation: false     # true = only user can trigger (/skill-name)
argument-hint: [arg1, arg2]         # shown in autocomplete
allowed-tools: Bash Read Write      # pre-approved tools (no permission prompt)
context: fork                       # isolated context (good for heavy tasks)
---

## Instructions for Claude

Write what Claude should DO, not what it IS.
Use headers to separate phases.
Be specific — vague instructions produce vague output.
```

## Frontmatter field guide

| Field | When to use |
|---|---|
| `disable-model-invocation: true` | Operational skills the user triggers manually (eod, audit, deploy) |
| `disable-model-invocation: false` | Knowledge skills Claude should auto-load when relevant |
| `context: fork` | Skills that do heavy file work and shouldn't pollute main context |
| `argument-hint` | Skills that take inputs (/reply [paste], /post [company]) |
| `allowed-tools` | Pre-approve Bash/Read/Write to skip permission prompts |

## Where to put skill files

| Path | Scope |
|---|---|
| `.claude/skills/{name}/SKILL.md` | This project only (committed to git — works in web sessions) |
| `~/.claude/skills/{name}/SKILL.md` | All projects on this machine (local only) |

**For Claude Code on the web: always use `.claude/skills/` in the repo.**

## Writing good skill instructions

1. **State the goal first** — one sentence on what this skill produces
2. **List inputs** — what context does Claude need to read?
3. **Write phases** — Step 1, Step 2, Step 3
4. **Specify output format** — show an example of what the output should look like
5. **Add a closing action** — what should Claude tell the user to do next?

## Common patterns

**Trigger + read + draft + write:**
Read a file → generate content → write output file → tell user what was created

**Trigger + ask + score + append:**
Ask questions → score against criteria → append to log file

**Auto-knowledge skill:**
No trigger needed — `disable-model-invocation: false` + a clear description = Claude loads it when relevant

## Response style

If the user wants to encode an SOP, ask them to describe the workflow in plain language, then draft the SKILL.md for them. Show the full file, ready to save.
