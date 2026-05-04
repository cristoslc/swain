---
source-id: "openclaw-daemon"
title: "OpenClaw — Always-On Personal AI Assistant Daemon"
type: repository
url: "https://github.com/openclaw/openclaw"
fetched: 2026-04-06T16:00:00Z
hash: "fbcd1be42726ebec14f54da4e9bd61bbf442eeb209063262437e6df4bd88b92b"
highlights:
  - "openclaw-daemon.md"
selective: true
notes: "Daemon-mode always-on agent; 20+ messaging channels; skills system; MCP via mcporter bridge; distinct from messaging-adapter angle in agentic-runtime-chat-adapters trove"
---

# OpenClaw — Always-On Personal AI Assistant Daemon

**Tagline:** OpenClaw is the AI that actually does things. It runs on your devices, in your channels, with your rules.

OpenClaw is a personal AI assistant you run on your own devices. It answers on the channels you already use (WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, BlueBubbles, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, WeChat, WebChat). It can speak and listen on macOS/iOS/Android, and can render a live Canvas.

## Install and daemon setup

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

The `--install-daemon` flag installs the Gateway as a launchd/systemd user service so it stays running. This is the always-on control pattern: the agent process persists and responds to incoming messages from any connected channel.

## Core architecture: the Gateway

The Gateway is the control plane. It:

- Maintains persistent connections to all configured messaging channels.
- Routes incoming messages to the AI model.
- Dispatches tool calls (via skills and MCP servers).
- Manages auth profile rotation and model failover.
- Exposes hook endpoints for permission management (via farmer integration).

```bash
openclaw gateway --port 18789 --verbose

# Direct agent invocation
openclaw agent --message "Ship checklist" --thinking high
```

## Runtime control model

OpenClaw's control loop is reactive rather than iterative:

- **Trigger**: incoming message on any connected channel.
- **Dispatch**: message → Gateway → AI model → tool calls.
- **Response**: AI response → back to originating channel.
- **Persistence**: daemon stays alive between messages; memory plugin maintains context.

This contrasts with the Ralph Wiggum loop (same prompt, repeated). OpenClaw is event-driven; Ralph is iteration-driven.

## Skills and plugins

Skills provide the assistant's capabilities. Most new skills go to ClawHub (`clawhub.ai`) rather than core. MCP servers integrate via the `mcporter` bridge rather than first-class MCP runtime in core.

```bash
# The awesome-openclaw-skills registry has 5,400+ community skills
# Core bundled skills cover baseline UX only
```

Key design decisions from VISION.md:

- No agent-hierarchy frameworks (manager-of-managers) as a default architecture.
- No heavy orchestration layers that duplicate existing agent and tool infrastructure.
- MCP integration via bridge (mcporter) to keep core lean and reduce MCP churn.
- Only one memory plugin active at a time.

## Security model

OpenClaw uses a deliberate security tradeoff: strong defaults without killing capability.

- Trust tiers: paranoid (approve everything), standard (auto-approve reads), autonomous (auto-approve most). These map directly to farmer's trust tier system.
- Secrets detection in CI (`.detect-secrets.cfg`).
- Sandboxed execution via `Dockerfile.sandbox`.
- Prompt injection risk mitigation: recommended to use "the strongest latest-generation model available" to reduce prompt injection risk.

## Multi-channel always-on pattern

```
┌─────────────────────────────────────────┐
│              OpenClaw Daemon            │
│                                         │
│  WhatsApp ──┐                           │
│  Telegram ──┤                           │
│  Slack ─────┼──▶ Gateway ──▶ AI Model  │
│  Discord ───┤        │                  │
│  Signal ────┘        │                  │
│                      ▼                  │
│              Skills / MCP Tools         │
└─────────────────────────────────────────┘
```

The daemon answers from any channel, maintains memory between sessions, and can perform computer-use tasks on the host machine.

## Sponsors

Sponsored by OpenAI, GitHub, NVIDIA, Vercel, Blacksmith, Convex. This signals commercial backing for the "always-on personal AI assistant" pattern.

## History

OpenClaw evolved through several names: Warelay → Clawdbot → Moltbot → OpenClaw. The name changes reflect evolution from a simple bot to a full personal AI assistant platform.

## Related trove

The `agentic-runtime-chat-adapters` trove covers OpenClaw as a messaging adapter in the ACP/ACPX protocol ecosystem. This source focuses on the daemon/always-on control loop angle.
