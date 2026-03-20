---
source-id: "claudefast-channels-guide"
title: "Claude Code Channels: Telegram & Discord Setup Guide (2026) — ClaudeFast"
type: web
url: "https://claudefa.st/blog/guide/development/claude-code-channels"
fetched: 2026-03-20T00:00:00Z
hash: "5e0d22ca1ec61be2fdbb68b0c4b800b074f5fa769248f1c2878aa40f4842bfb3"
---

# Claude Code Channels: Control Your Dev Sessions from Telegram and Discord

Claude Code Channels lets you message your coding sessions directly from Telegram or Discord. Your session processes requests with full filesystem, MCP, and git access, then replies through the same messaging app. Announced March 20, 2026 as a research preview.

## Channels vs Remote Control vs Web Sessions

Three ways to interact with Claude Code sessions remotely, solving different problems:

| Aspect | Channels | Remote Control | Web Sessions |
|--------|----------|----------------|--------------|
| **Interface** | Telegram, Discord (messaging apps) | claude.ai/code, iOS app, Android app | claude.ai/code browser |
| **Session location** | Your machine (local) | Your machine (local) | Anthropic cloud |
| **Setup** | Install plugin, create bot, pair | `claude remote-control` (one command) | Open claude.ai/code |
| **Best for** | Async messages, mobile-first, team channels | Continuing terminal sessions from phone | Quick tasks without local setup |
| **Local tools** | Full access (filesystem, MCP, git) | Full access (filesystem, MCP, git) | Cloud sandbox only |
| **Hackability** | High (plugin architecture, build your own) | Low (fixed interface) | None |
| **Notification style** | Native app notifications (Telegram/Discord) | Must open claude.ai or app | Must open claude.ai |
| **Team collaboration** | Discord guild channels for shared access | Single-user only | Single-user only |

**When to use Channels**: You want native mobile notifications, async workflows where you fire off requests and check back later, or team-based interaction through Discord guild channels. You also want Channels when you prefer a hackable, extensible system.

**When to use Remote Control**: You want the full claude.ai interface with rich formatting, file previews, and a familiar chat UI. Less setup (one command vs bot creation) and works immediately with the Claude mobile app.

As Thariq from the Claude Code team noted: "We want to give you a lot of different options in how you talk to Claude remotely. Channels is more focused on devs who want something hackable."

## How Channels Work Under the Hood

1. You install a channel plugin (Telegram or Discord) that runs as an MCP server
2. You launch Claude Code with the `--channels` flag, which activates the plugin
3. The MCP server connects to the messaging platform (polling for Telegram, WebSocket for Discord)
4. When a message arrives, the server wraps it as a `<channel>` event and pushes it into your session
5. Claude processes the request using your full local environment
6. Claude replies through tools exposed by the MCP server (`reply`, `react`, `edit_message`)

Security: sender allowlist per plugin + `--channels` flag per session + `channelsEnabled` org setting for Team/Enterprise.

If Claude hits a permission prompt while you're away, the session pauses until you approve locally. For unattended operation, `--dangerously-skip-permissions` bypasses prompts.

Claude's replies flow through the messaging platform's servers. For sensitive/proprietary work, the `fakechat` localhost option keeps everything on your machine.

## Telegram-Specific Features

- **Photos**: Inbound photos auto-downloaded to `~/.claude/channels/telegram/inbox/`. Send as "File" (long-press) for uncompressed originals
- **File attachments**: `reply` tool supports sending files back. Images inline; other types as documents. Max 50MB
- **Typing indicator**: Shows "botname is typing..." while Claude works
- **No message history**: Telegram Bot API doesn't expose history or search. Bot only sees real-time messages. Messages sent while session is down are lost

## Discord-Specific Features

- **Message history**: `fetch_messages` tool can pull recent history (up to 100 messages per call, oldest-first). Key differentiator — if session restarts, Claude can catch up on missed messages
- **Attachment handling**: Not auto-downloaded. Assistant sees metadata (name, type, size), calls `download_attachment` when needed
- **Guild channels**: Supports server/guild channels, not just DMs. Enables team collaboration
- **Custom emoji reactions**: `react` tool supports Unicode and custom emoji in `<:name:id>` format
- **Threading**: `reply` tool supports `reply_to` for native Discord threading

## Practical Use Cases

- **Monitor long-running tasks from phone**: Start build/test at desk, walk away, get notifications, send follow-ups
- **Quick fixes on the go**: Spot a typo in a PR on phone, message bot to fix and commit
- **Team collaboration through Discord**: Shared guild channel for pair-debugging with full codebase access
- **Async development workflows**: Combine with scheduled tasks — Claude runs tests hourly, reports through Telegram, waits for instructions on failure
- **AI executive assistant on Telegram**: Not just coding — calendar, email, CRM, project management via MCP connections
- **CI/CD notifications and reactions**: Forward CI results, Claude inspects logs, identifies issues, fixes or diagnoses

## Requirements and Limitations

### Requirements

- Claude Code v2.1.80 or later
- Bun runtime installed
- claude.ai authentication (Pro or Max plan). Console and API key auth not supported
- Team/Enterprise plans: admin must explicitly enable channels in managed settings

### Current Limitations

- **Session must stay running**: Close terminal and channel goes offline. Messages lost (Telegram) or queued (Discord via `fetch_messages`)
- **Permission prompts block remotely**: Pauses until approved at terminal
- **Allowlisted plugins only**: During preview, only `claude-plugins-official` accepted. Custom channels need `--dangerously-load-development-channels`
- **No persistent background mode**: Need to keep terminal session open. Workaround: tmux, screen, or background process
- **Platform-specific gaps**: Telegram has no message history. Discord requires more setup. Each platform's bot API has own constraints

Future platforms requested by community: Slack, WhatsApp, iMessage. Plugin architecture designed for expansion; community-built channels are part of the plan.
