---
source-id: cloudcli-claude-code-ui
type: web
url: "https://github.com/siteboon/claudecodeui"
title: "CloudCLI (aka Claude Code UI) — Desktop and Mobile UI for Claude Code, Cursor CLI, Codex, and Gemini CLI"
fetched: 2026-04-06T00:00:00Z
author: siteboon
---

# CloudCLI (aka Claude Code UI)

## Overview

CloudCLI is an open-source web and mobile UI for managing agentic coding sessions across multiple runtimes. It supports Claude Code, Cursor CLI, Codex, and Gemini CLI. Available as a self-hosted npm package or a managed cloud service at cloudcli.ai.

- **GitHub:** https://github.com/siteboon/claudecodeui
- **Stars:** 9,500+
- **License:** AGPL-3.0-or-later
- **Language:** TypeScript (63%), JavaScript (34%)
- **Releases:** 53 (latest v1.28.0, April 2026)
- **Commits:** 549

## Key features

- Responsive design for desktop, tablet, and mobile.
- Interactive chat interface for agent communication.
- Integrated shell terminal for direct CLI access.
- File explorer with syntax highlighting and live editing.
- Git explorer for staging, committing, and branch switching.
- Session management with resume, multi-session, and history tracking.
- Plugin system for custom tabs, backend services, and integrations.
- TaskMaster AI integration for project management (optional).
- Model compatibility across Claude, GPT, and Gemini families.

## Runtimes supported

- Claude Code.
- Cursor CLI.
- Codex (OpenAI).
- Gemini CLI.

## Session lifecycle

- Auto-discovers all sessions from `~/.claude` folder.
- Resume, manage multiple sessions, track history.
- CloudCLI Cloud keeps agents running when laptop is closed.

## Approval/permission flows

- All Claude Code tools disabled by default for safety.
- Selective tool enablement through settings UI.
- MCP server configuration managed via UI, synced with local config.

## Event normalization

- Unified interface across all four supported runtimes.
- Common chat, file, git, and terminal panels regardless of runtime.

## Architecture

- Self-hosted: `npx @cloudcli-ai/cloudcli` starts server on localhost:3001.
- CloudCLI Cloud: managed containerized environment, $7/month.
- Both use the operator's own AI subscriptions.
- Plugin architecture for extensibility.

## How it compares to Claude Code Remote Control

- CloudCLI shows all sessions, not just the active one.
- Settings changes in UI sync bidirectionally with `~/.claude` config.
- Works with more agents, not just Claude Code.
- Full UI (file explorer, git, shell), not just chat.
- Cloud version runs without a local machine staying on.

## Maturity assessment

Actively maintained with 549 commits and 53 releases. Strong community (9.5k stars, 1.3k forks, 135 open issues, 50 PRs). Commercial cloud offering suggests sustainable development. AGPL license may limit some integration patterns.
