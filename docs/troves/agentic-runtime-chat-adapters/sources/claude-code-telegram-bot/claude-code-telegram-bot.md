---
source-id: claude-code-telegram-bot
type: web
url: "https://github.com/RichardAtCT/claude-code-telegram"
title: "Claude Code Telegram Bot — Remote Access to Claude Code via Telegram"
fetched: 2026-04-06T00:00:00Z
author: RichardAtCT
---

# Claude Code Telegram Bot

## Overview

A Telegram bot that gives remote access to Claude Code. Supports natural language conversation, session persistence per project, webhook-driven automation, and scheduled tasks. Uses Claude Agent SDK as the primary integration with CLI fallback.

- **GitHub:** https://github.com/RichardAtCT/claude-code-telegram
- **Stars:** 2,400
- **License:** MIT
- **Language:** Python (99.6%)
- **Releases:** 7 (latest v1.6.0, March 2026)

## Runtimes supported

- Claude Code only (via claude-agent-sdk, with CLI fallback).

## Key features

- Agentic mode (default): natural language conversation, no commands needed.
- Classic mode: 13-command terminal-like interface.
- Session persistence per user/project directory in SQLite.
- Multi-layer authentication (whitelist + optional token-based).
- Directory sandboxing with path traversal prevention.
- File and image upload handling.
- Voice message transcription (Mistral Voxtral / OpenAI Whisper / local whisper.cpp).
- Git integration with safe repository operations.
- Quick actions system with context-aware buttons.
- Session export in Markdown, HTML, and JSON.
- 16 configurable tools with allowlist/disallowlist control.
- Tunable verbosity levels (0=quiet, 1=normal, 2=detailed).

## Session lifecycle

- Automatic session persistence per user/project directory.
- `/new` to start fresh, `/continue` to resume.
- `/repo` to switch between cloned repositories.
- Sessions auto-resume when switching back to a project.

## Approval/permission flows

- Tool allowlist/disallowlist control via configuration.
- Directory sandboxing restricts access to approved paths.
- Rate limiting with token bucket algorithm.
- Cost tracking per user with configurable spending limits.

## Event-driven automation

- Webhook server for GitHub events (push, PR, issues).
- Cron scheduler for recurring Claude tasks.
- Notification service with per-chat rate limiting.
- Event bus for decoupled message routing.

## Architecture

- Python 3.11+ with Poetry.
- python-telegram-bot for Telegram integration.
- claude-agent-sdk for Claude Code integration.
- SQLite for persistence and migrations.
- FastAPI for webhook API server.
- Systemd setup guide for production deployment.

## Maturity assessment

Well-structured project with 226 commits, 7 releases, good documentation including security policy and systemd guide. Actively maintained. Claude Code-only limits its usefulness as a general adapter. Designed as a complete product, not a composable library.

## Relevance to build-vs-buy

Demonstrates a solid pattern for Telegram-to-Claude-Code bridging with session management, auth, and webhooks. However, locked to Claude Code and Telegram. Not runtime-agnostic. Useful as a reference implementation for one specific platform/runtime pairing.
