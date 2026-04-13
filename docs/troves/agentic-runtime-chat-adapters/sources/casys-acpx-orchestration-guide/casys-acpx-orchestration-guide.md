---
source-id: casys-acpx-orchestration-guide
type: web
url: "https://casys.ai/blog/acpx-multi-agent-orchestration"
title: "ACPX Inside Claude Code: Practical Multi-Agent Orchestration"
fetched: 2026-04-06T00:00:00Z
author: casys.ai
---

# ACPX Inside Claude Code: Practical Multi-Agent Orchestration

## Overview

A hands-on guide explaining how ACPX replaces PTY scraping with structured protocol-based communication between AI coding agents. Covers the practical integration of ACPX with Claude Code and cmux for multi-agent orchestration.

- **URL:** https://casys.ai/blog/acpx-multi-agent-orchestration

## Key insights

### Why ACPX matters over subagents

- Claude Code subagents share the same model provider, billing, and context window. A subagent cannot be a Codex or Gemini instance; it is always Claude.
- Agent Teams let multiple Claude Code sessions coordinate, but they are still Claude-only.
- ACPX breaks the vendor boundary: Claude Code can orchestrate Codex for Python tests while Gemini CLI reviews the Go backend.

### Structured vs. raw output

- When a subagent returns a result, you get a text blob.
- When an ACPX session returns a result, you get structured events: which tool was called, what files were modified, what the agent's reasoning was.

### Practical setup with cmux

- Three-pane layout: Claude Code (orchestrator), secondary agent (Codex/Gemini), dev server or test runner.
- cmux notifications when ACPX sessions finish.
- `cmux read-screen` for reading terminal output from any pane.

### OpenClaw + ACPX integration

- User sends message in Telegram.
- OpenClaw receives it.
- Gemini classifies it as a coding task.
- ACPX plugin spawns a headless Codex instance through its ACP adapter.
- Result streams back to chat.

## Relevance to build-vs-buy

Provides the practical architecture pattern for runtime-agnostic agent orchestration. The OpenClaw -> ACPX -> coding agent pipeline is essentially the Untethered Operator pattern implemented with existing tools. The structured event model (vs. PTY scraping) is architecturally aligned with what swain needs.
