---
source-id: omo-slim-mcps
title: oh-my-opencode-slim — MCP Servers
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/mcps.md
fetched: 2026-05-05
type: documentation
---

# MCP Servers

## Built-in MCPs

| MCP | Purpose | Endpoint |
|-----|---------|----------|
| `websearch` | Real-time web search via Exa AI | `https://mcp.exa.ai/mcp` |
| `context7` | Official library documentation (up-to-date) | `https://mcp.context7.com/mcp` |
| `grep_app` | GitHub code search via grep.app | `https://mcp.grep.app` |

## Default Permissions Per Agent

| Agent | Default MCPs |
|-------|-------------|
| `orchestrator` | `*`, `!context7` |
| `librarian` | `websearch`, `context7`, `grep_app` |
| `designer` | none |
| `oracle` | none |
| `explorer` | none |
| `fixer` | none |
| `councillor` | none |

## Configuring MCP Access

Syntax in preset config `mcps` array:

| Syntax | Meaning |
|--------|---------|
| `["*"]` | All MCPs |
| `["*", "!context7"]` | All except context7 |
| `["websearch", "context7"]` | Only listed |
| `[]` | No MCPs |
| `["!*"]` | Deny all |

Rules: `*` expands to all available; `!item` excludes; conflicts → deny wins.

## Global MCP Disable

Add to root config: `"disabled_mcps": ["websearch"]` to cut external network calls entirely (air-gapped or cost control).
