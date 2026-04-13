---
source-id: acpx-agent-client-protocol
type: web
url: "https://github.com/openclaw/acpx"
title: "ACPX — Headless CLI Client for Agent Client Protocol (ACP) Sessions"
fetched: 2026-04-06T00:00:00Z
author: openclaw
---

# ACPX

## Overview

ACPX is a headless CLI client for the Agent Client Protocol (ACP). It replaces PTY scraping with structured protocol communication between AI coding agents. One command surface for Pi, OpenClaw ACP, Codex, Claude, Gemini, and 10+ other ACP-compatible agents.

- **GitHub:** https://github.com/openclaw/acpx
- **Stars:** 2,000
- **License:** MIT
- **Language:** TypeScript (95%)
- **Status:** Alpha (CLI/runtime interfaces may change)
- **Releases:** 20 (latest v0.5.0, April 2026)

## Built-in agent adapters

| Agent | Adapter | Wraps |
|-------|---------|-------|
| pi | pi-acp | Pi Coding Agent |
| openclaw | native (openclaw acp) | OpenClaw ACP bridge |
| codex | codex-acp | Codex CLI |
| claude | claude-agent-acp | Claude Code |
| gemini | native (gemini --acp) | Gemini CLI |
| cursor | native (cursor-agent acp) | Cursor CLI |
| copilot | native (copilot --acp --stdio) | GitHub Copilot CLI |
| droid | native (droid exec --output-format acp) | Factory Droid |
| iflow | native (iflow --experimental-acp) | iFlow CLI |
| kilocode | npx @kilocode/cli acp | Kilocode |
| kimi | native (kimi acp) | Kimi CLI |
| kiro | native (kiro-cli-chat acp) | Kiro CLI |
| opencode | npx opencode-ai acp | OpenCode |
| qoder | native (qodercli --acp) | Qoder CLI |
| qwen | native (qwen --acp) | Qwen Code |
| trae | native (traecli acp serve) | Trae CLI |

## Key capabilities

- Persistent sessions: multi-turn conversations that survive across invocations, scoped per repo.
- Named sessions: parallel workstreams in the same repo.
- Prompt queueing: submit prompts while one is already running.
- Cooperative cancel: ACP `session/cancel` without tearing down state.
- Crash reconnect: dead agent processes detected, sessions reloaded automatically.
- Structured output: typed ACP messages (thinking, tool calls, diffs) instead of ANSI scraping.
- One-shot mode: `exec` for stateless fire-and-forget tasks.
- Experimental flows: TypeScript workflow modules over multiple prompts.
- Auth handshake: stable `authenticate` support via env/config credentials.
- Permission controls: `--approve-all`, `--approve-reads`, `--deny-all`.

## Session lifecycle

- `sessions new`: create fresh session.
- `sessions ensure`: idempotent (return existing or create).
- `sessions close`: soft-close (terminate processes, keep record).
- Prompt commands route by walking from cwd to nearest git root.
- Session metadata stored under `~/.acpx/sessions/`.
- Turn history previews appended to session metadata.
- Queue owner TTL for follow-up prompts.

## Event normalization

- Structured ACP messages instead of raw ANSI streams.
- NDJSON output format for automation.
- Stable envelope with sessionId, requestId, seq, stream, type.
- Event types: thinking, tool_call, diff, etc.

## Flows (experimental)

- `acp` steps for model work.
- `action` steps for deterministic mechanics (shell, GitHub calls).
- `compute` steps for local routing.
- `checkpoint` steps for external pauses.
- Workspace isolation: per-step cwd for disposable worktrees.

## Maturity assessment

Alpha status with 267 commits and 20 releases. Active development under the OpenClaw organization. MIT license. The key risk is alpha instability, but the protocol approach is architecturally sound and already supports 16 coding agents. This is the closest existing project to a "universal runtime adapter."

## Relevance to build-vs-buy

ACPX is the strongest candidate for a runtime adapter layer. It normalizes session lifecycle, permissions, and event streams across 16 agents via ACP. The alpha status is the main risk. Could be used as a component library for the adapter layer of Untethered Operator.
