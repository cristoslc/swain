---
source-id: "claudefast-remote-control-guide"
title: "Claude Code Remote Control: Continue Local Sessions from Your Phone — ClaudeFast"
type: web
url: "https://claudefa.st/blog/guide/development/remote-control-guide"
fetched: 2026-03-20T00:00:00Z
hash: "aa49ecc20316cafa6b5caa20a3a193034ee39dc24d20d3c5c13fe8e539cdee2c"
---

# Claude Code Remote Control: Continue Local Sessions from Your Phone

Remote Control (February 2026, research preview) bridges your local Claude Code terminal session with claude.ai/code, Claude iOS app, and Claude Android app. It's a synchronization layer, not a cloud migration.

Your local setup is irreplaceable — CLAUDE.md configuration, custom skills, file access, and MCP integrations all stay available. A cloud session starts fresh. Remote Control keeps everything.

## How It Works Under the Hood

- Local session makes **outbound HTTPS requests only** — no inbound ports
- Registers with Anthropic API and polls for work
- Server routes messages between web/mobile client and local session over streaming connection
- All traffic flows through Anthropic API over TLS
- Multiple short-lived credentials, each scoped to a single purpose
- Files and MCP servers never leave your machine — only chat messages and tool results flow through the encrypted bridge

## Remote Control vs OpenClaw

| Aspect | Remote Control | OpenClaw |
|--------|----------------|----------|
| **Setup** | `claude remote-control` (one command) | Self-hosted, requires port forwarding or tunnel config |
| **Security** | Outbound-only HTTPS, no open ports, TLS, short-lived credentials | WebSocket-based, CVE-2026-25253 RCE vulnerability affected 50K+ instances |
| **Platforms** | claude.ai/code, iOS, Android | WhatsApp, Telegram, Discord, Slack, 15+ platforms |
| **Scope** | Coding-focused (terminal, files, MCP) | General-purpose (calendar, email, smart home, everything) |
| **Cost** | Included with Pro/Max subscription | Free (self-hosted), but bring your own API keys |
| **Reconnection** | Automatic when laptop wakes from sleep | Manual restart on connection loss |
| **Permissions** | Full Claude Code permission model | Broad system access by default |

Fundamental difference: Remote Control is a secure, purpose-built bridge for development workflows. OpenClaw is a general-purpose life assistant.

## Practical Workflows

### The "Walk Away" Pattern
Start a complex multi-agent task at desk, monitor and steer from phone while away. Agents keep running locally with full tool access.

### The "Couch Review" Pattern
Queue up code reviews or test runs at workstation, review results and approve actions from couch. Useful with async workflows.

### The "Multi-Device" Pattern
Start from terminal for heavy coding, switch to browser for lighter interactions, phone for quick approvals. Conversation stays in sync.

### Pair It with Worktrees
Combine Remote Control with git worktrees. Start an isolated worktree session, enable remote control, manage it from anywhere. Main branch untouched.

## Current Limitations

- One session at a time per Claude Code instance
- Terminal must stay open (close = session ends)
- ~10 minute network timeout
- Permission approval still required remotely (--dangerously-skip-permissions reportedly doesn't work with RC yet)
- Pro and Max plans only (not available on Team/Enterprise at launch, but now available with admin toggle)

## What's Next

Remote Control launched alongside Cowork (scheduled tasks), signaling push toward persistent, always-available development companion. Current limitations point toward fully cloud-hosted Remote Control that doesn't depend on machine being awake.

Community's most common request: iMessage support for Channels, and a fully persistent daemon mode for Remote Control.
