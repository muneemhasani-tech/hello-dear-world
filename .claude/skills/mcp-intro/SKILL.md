---
name: mcp-intro
description: Explain how MCP (Model Context Protocol) works and how to connect Claude to external tools. Triggers on "MCP", "connect Claude to", "integrate with", "how do I give Claude access to", "CRM integration", "scraper integration".
disable-model-invocation: false
---

## What This Skill Does

Explains MCP and guides connecting Claude to external tools and data sources relevant to the NINE outreach pipeline.

## What MCP is

MCP (Model Context Protocol) is a standard that lets Claude connect to external tools, APIs, and data sources. Instead of copying data into the chat, Claude can read from and write to live systems directly.

In Claude Code, MCP servers appear as tools Claude can call during a session.

## How to connect an MCP server

In your Claude Code settings (`~/.claude/settings.json` or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "tool-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

## Relevant MCP servers for NINE

| Tool | MCP server | Use case |
|---|---|---|
| GitHub | `@modelcontextprotocol/server-github` | Read/write repo files, manage workflows |
| Google Drive | `@modelcontextprotocol/server-gdrive` | Access brand assets, share docs |
| Gmail | Via Zapier or native MCP | Read replies, send follow-ups |
| Notion | `@modelcontextprotocol/server-notion` | CRM in Notion, project tracking |
| Sheets | Via Apps Script or Zapier | Revenue tracking, lead lists |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web research in pipeline |

## What's already connected in this session

Check the available tools at the start of a session — MCP tools appear prefixed with `mcp__`. The GitHub MCP (`mcp__github__*`) is connected and scoped to this repo.

## When to use MCP vs scripts

- **MCP** — interactive sessions, ad-hoc queries, when Claude needs to read live data mid-conversation
- **Scripts** (`research_leads.py`, `analyze_leads.py`) — scheduled/automated runs, no human in the loop

## Response style

Be practical. If they want to connect a specific tool, walk through the exact config needed. Point out which tools are already connected in this session.
