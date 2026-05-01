---
title: "ACPX — Headless CLI Client for ACP Sessions"
source-url: "https://github.com/openclaw/acpx"
fetch-date: "2026-05-01"
type: web-page
publisher: "OpenClaw"
---

# ACPX — Headless Agent Client Protocol Client

## Overview

acpx is a headless CLI client for the Agent Client Protocol (ACP). It lets AI agents and orchestrators talk to coding agents over a structured protocol instead of PTY scraping. One command surface for Pi, OpenClaw ACP, Codex, Claude, Gemini CLI, OpenCode, and other ACP-compatible agents.

## Architecture Pattern

```
acpx pi 'review recent changes'
acpx openclaw exec 'summarize active session state'
acpx codex 'fix the failing typecheck'
acpx claude 'refactor auth middleware'
```

## Key Design Decisions

- Headless execution — no TTY to approve permission prompts.
- ACPX permission profiles control what operations the harness can perform without prompting.
- Sessions survive gateway restarts — task picks up where it left off.
- Each coding agent gets its own working directory with isolated conversations.

## Cross-Harness Compatibility

The protocol layer (ACP) abstracts away agent-specific behavior. The tool (acpx) provides a uniform CLI surface regardless of which coding agent runs underneath. This is the tool-over-skill pattern: a standalone executable that orchestrates agent sessions rather than injecting text instructions into the context window.

## Permission Modes

Non-interactive sessions cannot click native permission prompts. Write/exec-heavy coding runs need ACPX permission profiles that can proceed headlessly. The tool defines what's allowed, not the agent's context window.
