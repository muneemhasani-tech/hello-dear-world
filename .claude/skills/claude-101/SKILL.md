---
name: claude-101
description: Answer questions about Claude features, projects, artifacts, research mode, memory, and how to get better results. Triggers on questions like "how do I use Claude", "what are projects", "what is research mode", "how do artifacts work", "how do I get Claude to remember things".
disable-model-invocation: false
---

## What This Skill Does

Answers questions about using Claude effectively. Covers core features, productivity patterns, and how to get better results from Claude in daily work.

## Key topics

### Projects
- Projects give Claude persistent context across conversations
- Add files, instructions, and knowledge to a project — Claude reads them at the start of every session
- Best for: ongoing work, recurring workflows, team knowledge bases
- CLAUDE.md in a repo = project-level instructions for Claude Code

### Artifacts
- Claude can generate files, code, documents, and structured outputs
- Ask Claude to "write this as a file" or "create a document" to get a downloadable artifact
- In Claude.ai, artifacts appear in a side panel

### Research mode
- Claude can search the web and synthesise information from multiple sources
- Use for: market research, competitor analysis, fact-checking, summarising topics
- Trigger: "research X" or "search for Y"

### Memory and persistence
- Claude doesn't remember between conversations by default
- Use Projects to persist context
- In Claude Code: CLAUDE.md carries instructions; skill files carry SOPs
- For personal preferences: add them to your project instructions

### Getting better results
- Be specific: include context, constraints, and the format you want
- Give examples: show Claude what "good" looks like
- Iterate: ask Claude to revise, not just regenerate
- Use system prompts / CLAUDE.md to set standing instructions
- Break complex tasks into steps — Claude is better at one clear task at a time

### Claude Code specifics
- Claude Code is the CLI version of Claude for software engineering
- Reads CLAUDE.md for project context
- Skills (`/skill-name`) run reusable workflows
- Works best with clear task descriptions and access to the relevant files

## Response style

Answer the specific question asked. Keep it practical — what to do, not just what it is. If the question is vague, ask one clarifying question before answering.
