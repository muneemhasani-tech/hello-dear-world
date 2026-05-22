---
name: claude-api
description: Help with building automations and apps using the Claude API / Anthropic SDK. Triggers on questions about "Claude API", "Anthropic API", "tool use", "structured output", "RAG", "pipelines", "prompt caching", or building AI-powered scripts.
disable-model-invocation: false
---

## What This Skill Does

Guides building with the Claude API and Anthropic SDK. Covers API usage patterns, tool use, structured output, pipelines, and prompt caching for the NINE outreach automation context.

## Key patterns

### Basic API call (Python)
```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Your prompt here"}]
)
print(message.content[0].text)
```

### Prompt caching (use for repeated context)
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "Your large system prompt here...",
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "Question"}]
)
```
Use caching when the same large context (brand knowledge, lead data) is sent in many calls.

### Tool use (structured actions)
Define tools Claude can call; parse the result to take action. Useful for: web search, CRM updates, file writes.

### Structured output
Use `response_format` or ask Claude to return JSON. Validate with Pydantic or manual parsing.

### Pipelines
Chain API calls: one call classifies, next call drafts, next call formats. Keep each call single-purpose.

## NINE-specific use cases

- Batch email drafting: send all 5 leads in one call with a list, get 5 emails back
- Lead scoring: send sitemap data, get a gap score + pricing tier
- Reply classification: send a pasted reply, get stage + next message
- Brand voice check: send a draft email, get a pass/fail + rewrite

## Models (current)

- `claude-opus-4-7` — most capable, use for drafting and complex reasoning
- `claude-sonnet-4-6` — fast and capable, use for classification and pipelines
- `claude-haiku-4-5-20251001` — fastest, use for simple transforms and scoring

## Response style

Give working code snippets. Adapt to the NINE pipeline context where relevant. Flag cost implications of model choice.
