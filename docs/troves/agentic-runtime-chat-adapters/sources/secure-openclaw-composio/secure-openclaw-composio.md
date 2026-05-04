---
source-id: secure-openclaw-composio
type: web
url: "https://github.com/ComposioHQ/secure-openclaw"
title: "Secure OpenClaw — Claude-Powered AI Assistant on Messaging Platforms with Composio"
fetched: 2026-04-06T00:00:00Z
author: ComposioHQ
---

# Secure OpenClaw

## Overview

A personal AI assistant built on Claude Code and OpenCode, deployed to messaging platforms (WhatsApp, Telegram, Signal, iMessage) with 500+ app integrations via Composio. Demonstrates the pattern of wrapping coding runtimes behind a messaging gateway with approval flows.

- **GitHub:** https://github.com/ComposioHQ/secure-openclaw

## Runtimes supported

- Claude Code.
- OpenCode (auto-detected server on port 4096).

## Messaging platforms

- WhatsApp.
- Telegram.
- Signal.
- iMessage.

## Approval/permission flows

- Interactive approval via messaging: "Claude wants to use Bash. Reply Y to allow, N to deny."
- Numbered options for clarifying questions.
- 2-minute approval timeout.

## Key features

- Persistent memory at ~/secure-openclaw/.
- Cron-based scheduling for reminders and recurring tasks.
- Docker deployment with persistent volumes.
- Composio integration for 500+ external apps.

## Architecture

- Gateway pattern: messaging platform -> gateway -> coding runtime.
- Claude Code and OpenCode run inside Docker container.
- WhatsApp auth and memory persisted in Docker volumes.

## Maturity assessment

Backed by Composio (commercial company). Focuses on security and ease of deployment. The approval flow pattern (Y/N via messaging) is a useful reference for implementing runtime approval delegation through chat.

## Relevance to build-vs-buy

Demonstrates approval-flow-over-chat pattern specifically for coding runtimes. The "Reply Y/N" approach for tool permissions through messaging is directly relevant to Untethered Operator. Limited to two runtimes. The Composio integration adds breadth for non-coding tools.
