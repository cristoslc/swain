---
source-id: openclaw-ai-assistant
type: web
url: "https://github.com/openclaw/openclaw"
title: "OpenClaw — Personal AI Assistant across 15+ Messaging Platforms"
fetched: 2026-04-06T00:00:00Z
author: Peter Steinberger / OpenClaw Foundation
---

# OpenClaw

## Overview

OpenClaw (formerly Clawdbot, then Moltbot) is a self-hosted AI agent runtime that connects to 15+ messaging platforms. Created by Peter Steinberger (PSPDFKit founder), it reached 247,000 GitHub stars by March 2026. Steinberger joined OpenAI in February 2026, and a non-profit foundation now stewards the project.

- **GitHub:** https://github.com/openclaw/openclaw
- **Stars:** 247,000+
- **License:** Open source
- **Ecosystem:** 40+ templates, weekly releases

## Messaging platforms supported

- WhatsApp.
- Telegram.
- Discord.
- Slack.
- Signal.
- iMessage (macOS-only via imsg).
- Google Chat.
- Microsoft Teams (Bot Framework).
- Matrix.
- IRC.
- BlueBubbles.
- Feishu.
- LINE.
- Mattermost.
- Nextcloud Talk.
- Nostr.
- Synology Chat.
- Tlon.
- Twitch.
- Zalo.
- WeChat (via official Tencent plugin).
- WebChat.

## Architecture

- Node.js long-running service.
- Agent Core handles message processing and conversation context.
- Model Router provides unified BYOK interface for OpenAI, Anthropic, Google, DeepSeek, and local models.
- Platform Adapters provide native integrations per messaging surface.
- Memory Layer stores persistent conversations with configurable retention and vector search.
- Plugin system for tools, skills, and integrations.
- ACP (Agent Client Protocol) plugin enables delegation to external coding agents.

## Runtime support

- Not itself a coding runtime, but orchestrates coding agents via ACPX plugin.
- Via ACP integration: Claude Code, Codex, Gemini CLI, OpenCode, Pi, Kimi.
- ClawRouters for cost optimization across models.

## Session lifecycle

- Persistent 24/7 operation as a daemon.
- Persistent memory across sessions.
- `openclaw onboard --install-daemon` for daemon setup.
- Gateway mode on port 18789.

## Approval/permission flows

- Exec approvals with durable trust model (`allow-always` persists).
- `exec-approvals.json` for allowlist management.
- Tools.exec policy enforcement.
- `openclaw doctor` for configuration validation.

## Security concerns

- CVE-2026-25253: RCE vulnerability via WebSocket affecting 50K+ instances.
- Chinese authorities restricted government use due to security risks.
- Maintainer warned about danger for non-technical users.

## Maturity assessment

Most popular self-hosted AI agent project by stars. Weekly releases, large community, foundation governance. However, general-purpose assistant focus means coding agent integration is a secondary concern handled through the ACPX plugin layer.

## Relevance to build-vs-buy

OpenClaw is the messaging platform router, not the coding agent adapter. Its value is the 15+ platform adapters and persistent memory layer. The ACPX plugin bridges it to coding runtimes. For swain, OpenClaw would be the "chat surface" layer, with ACPX as the glue to coding agents.
