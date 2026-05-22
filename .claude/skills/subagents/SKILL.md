---
name: subagents
description: Explain how to delegate tasks to subagents, run parallel work, and build multi-step workflows with Claude. Triggers on "subagents", "delegate to", "run in parallel", "multi-agent", "Agent tool", "background agent".
disable-model-invocation: false
---

## What This Skill Does

Explains how to use Claude subagents for parallelising tasks, protecting context, and automating multi-step workflows.

## What subagents are

A subagent is a separate Claude instance you spin up to handle a specific task. The parent agent delegates, the subagent works, and returns a result. Subagents have no memory of the parent's conversation — they start fresh with whatever prompt you give them.

## When to use subagents

- **Parallel independent tasks** — research 5 companies at the same time, not one after another
- **Context protection** — heavy file reads or long outputs go in the subagent, not the main context
- **Specialised work** — one subagent for research, another for drafting, another for formatting

## When NOT to use subagents

- Simple single-step tasks — just do it inline
- Tasks where you need the result to inform the next step before the agent can finish (use sequential calls instead)
- When the subagent would need context from the parent conversation (brief it explicitly)

## Agent tool usage (Claude Code SDK)

```python
Agent({
    description: "Research leads for Austin restaurants",
    prompt: "Search DuckDuckGo for restaurant businesses in Austin TX. Return 10 results with name, website, and a one-line pitch angle for motion graphics outreach.",
    subagent_type: "general-purpose",
    run_in_background: False  # True if you don't need result immediately
})
```

## Parallel agents

Send multiple Agent tool calls in a single message — they run concurrently:

```
Agent(research leads for city A)   ← these run at the same time
Agent(research leads for city B)   ← 
Agent(research leads for city C)   ←
```

## Briefing a subagent well

- State the goal explicitly — it hasn't seen your conversation
- Include all needed context in the prompt (file paths, data, constraints)
- Specify the output format — "return a markdown table with columns: Name, Website, Niche"
- Say whether it should write files or just return results

## Background agents

Set `run_in_background: True` when:
- The task takes a while and you want to continue with other work
- You'll be notified when it completes

## NINE pipeline use case

Parallelise city research: spin up 3 subagents for 3 cities simultaneously instead of running `research_leads.py` sequentially. Each subagent searches one city and returns a leads list.

## Response style

Give working examples. If user has a specific task to parallelise, sketch the agent architecture for them.
