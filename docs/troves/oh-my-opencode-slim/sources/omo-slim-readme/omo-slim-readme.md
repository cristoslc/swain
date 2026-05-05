---
source-id: omo-slim-readme
title: oh-my-opencode-slim — README
url: https://github.com/alvinunreal/oh-my-opencode-slim
fetched: 2026-05-05
type: repository
author-name: Alvin Unreal (Boring Dystopia Development)
---

# oh-my-opencode-slim

A slimmed, cleaned, and fine-tuned fork of oh-my-opencode that consumes far fewer tokens. Agent orchestration plugin for OpenCode.

## Overview

An open multi-agent suite for OpenCode that mixes any models and auto-delegates tasks. Includes a built-in team of seven specialized agents (plus one optional) that scout codebases, look up documentation, review architecture, handle UI work, and execute well-scoped implementation tasks under a master orchestrator.

The core idea: instead of forcing one model to do everything, route each part of the job to the best-suited agent, balancing quality, speed, and cost.

## Installation

```
bunx oh-my-opencode-slim@latest install
```

The installer registers the companion TUI plugin in OpenCode's `tui.json`, adding a sidebar showing specialist-agent status and active/reusable task sessions.

For manual setups, add `oh-my-opencode-slim` to the `plugin` array in both `opencode.json` and `tui.json`.

### Presets

The installer generates both OpenAI and OpenCode Go presets, with OpenAI active by default:
- OpenAI: `openai/gpt-5.5` for higher-judgment agents, `openai/gpt-5.4-mini` for faster scoped agents
- OpenCode Go: `opencode-go/glm-5.1`, `opencode-go/deepseek-v4-pro`, etc.

## Agent Roster

### Core Agents (7)

1. **Orchestrator** — Master delegator and strategic coordinator. Default: `openai/gpt-5.5`. Strongest all-around coding model; both main coding agent and delegator.
2. **Explorer** — Codebase reconnaissance. Default: `openai/gpt-5.4-mini`. Fast, low-cost model for broad scouting.
3. **Oracle** — Strategic advisor and debugger of last resort. Default: `openai/gpt-5.5 (high)`. Strongest high-reasoning model for architecture, hard debugging, code review.
4. **Council** — Multi-LLM consensus engine. Runs multiple councillors in parallel, synthesizes their views. Costly; manual invocation recommended.
5. **Librarian** — External knowledge retrieval. Default: `openai/gpt-5.4-mini`. Documentation lookups and web research.
6. **Designer** — UI/UX implementation and visual excellence. Default: `openai/gpt-5.4-mini`. Frontend polish.
7. **Fixer** — Fast implementation specialist. Default: `openai/gpt-5.4-mini`. Bounded execution and test writing.

### Optional Agent

- **Observer** — Visual analysis for images, PDFs, diagrams. Disabled by default. Saves main context tokens by processing raw files offloaded from orchestrator.

## Docs Map

- Installation Guide, Configuration, Council, Multiplexer, Session Management, Todo Continuation, Preset Switching, Codemap, Skills, MCPs, Tools, Interview, Divoom Display

## Tech Stack

TypeScript, Bun, Biome. MIT license.

## Metrics

- 3.9k stars, 268 forks, 488 commits, 37 releases (latest: v1.0.6, Apr 30 2026)
- 468 tests across 35 files
