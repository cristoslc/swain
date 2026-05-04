---
source-id: "grainulation-farmer"
title: "Farmer — Approve AI Agent Tool Calls from Anywhere"
type: repository
url: "https://github.com/grainulation/farmer"
fetched: 2026-04-06T15:00:00Z
hash: "3ee36fb4427d46416ee1ad1216dac2c3b48927748cd32c6fc8e40d0c27cb0f21"
highlights:
  - "grainulation-farmer.md"
selective: true
notes: "Remote permission dashboard for AI agents; Claude Code hook adapter ships first"
---

# Farmer — Approve AI Agent Tool Calls from Anywhere

**Tagline:** Approve AI agent tool calls from anywhere.

Farmer sits between your AI coding agent and your terminal, giving you a visual dashboard to approve, deny, or respond to tool calls in real time. It supports desktop and mobile.

## Install

```bash
npm install -g @grainulation/farmer
```

## Quick start

```bash
# 1. Install hooks (once)
farmer connect --global   # all projects, or:
farmer connect            # current project only

# 2. Start the dashboard
farmer start

# 3. Open the token URL printed to the terminal

# 4. Start Claude in any project — hooks route automatically
```

## Features

- **Desktop + mobile dashboard** — session sidebar, permission cards with syntax-highlighted code, activity feed, mobile swipe card view.
- **Agent-agnostic hook protocol** — Claude Code adapter ships first; write your own for other agents.
- **Multi-session** — manage multiple AI sessions from one dashboard.
- **Multi-user roles** — admin and viewer tokens with separate permissions; viewers see read-only cards.
- **Trust tiers** — paranoid (approve everything), standard (auto-approve reads), autonomous (auto-approve most).
- **AskUserQuestion** — deny-to-respond pattern lets you answer agent questions from the dashboard.
- **Security** — two-token auth (admin + viewer), HMAC-signed invite links with expiry, CSRF protection, CSP headers, audit logging.
- **Data persistence** — activity and messages survive server restarts.
- **Stale server guard** — auto-approves when no dashboard is connected (prevents CLI blocking).

## CLI

```bash
farmer start [--port 9090] [--token <secret>] [--viewer-token <secret>] [--trust-proxy] [--data-dir <path>]
farmer stop
farmer status
```

## Hook protocol

Farmer exposes four hook endpoints (localhost only):

| Endpoint | Purpose |
|----------|---------|
| `/hooks/permission` | Tool permission requests (blocking — waits for approve/deny) |
| `/hooks/activity` | Tool completion events (non-blocking) |
| `/hooks/notification` | Messages, questions, agent events (non-blocking) |
| `/hooks/lifecycle` | Session start/end events |
| `/hooks/stop` | Graceful shutdown signal |

## Adapter interface

Extend `BaseAdapter` in `lib/adapters/base.js` to support a new AI agent. Methods: `name`, `parseRequest`, `formatResponse`, `getToolName`, `isQuestion`, `parseNotification`.

## Architecture

```
bin/farmer.js          CLI entry point (start/stop/status)
lib/server.js          Core HTTP + SSE server
lib/adapters/          Agent adapter interface + Claude Code adapter
lib/persistence.js     State persistence (atomic write, debounced)
lib/connect.js         One-step hook installation and settings.json management
lib/security.js        Token auth, CSRF, CSP, PID lock, audit log
public/index.html      Dashboard (inline JS, no build step)
```

## Zero dependencies

Farmer has zero npm dependencies. SSE for real-time streaming, polling as fallback.

## License

MIT
