---
source-id: omo-features
type: web
url: "https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/features.md"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — Features Reference"
---

# Oh-My-OpenAgent Features Reference

## 11 Specialized Agents

Core agents with deterministic tab cycling in order: Sisyphus (1), Hephaestus (2), Prometheus (3), Atlas (4).

### Core Agents
- **Sisyphus**: Main orchestrator. Claude Opus 4.7 (or Kimi K2.5 / GLM 5). Plans, delegates, aggressive parallel execution. Todo-driven with extended thinking (32k budget).
- **Hephaestus**: Autonomous deep worker. GPT-5.4 only. Goal-oriented, explores codebase, executes end-to-end. Cannot be moved to Claude — built for GPT's principle-driven style.
- **Oracle**: Read-only architecture/debugging consultant. GPT-5.4 preferred, Gemini 3.1 Pro and Claude Opus as fallbacks.
- **Librarian**: Multi-repo analysis, documentation lookup. MiniMax M2.7 — speed over intelligence.
- **Explore**: Fast codebase grep. Grok Code Fast 1 — speed over depth.
- **Multimodal Looker**: Vision/screenshot analysis. GPT-5.4 preferred.

### Planning Agents
- **Prometheus**: Strategic planner with interview mode. Auto-detects model family and switches prompts.
- **Metis**: Pre-planning gap analyzer. Identifies hidden intentions and AI failure points.
- **Momus**: Ruthless plan reviewer. GPT-5.4 xhigh. Validates against clarity, verifiability, and context standards.

### Orchestration Agents
- **Atlas**: Todo-list orchestrator. Systematic task execution with learnings accumulation.
- **Sisyphus-Junior**: Category-spawned executor. Model selected by category. Cannot re-delegate (prevents infinite loops).

## Tool Restrictions

| Agent | Restrictions |
|-------|-------------|
| oracle | Read-only: cannot write, edit, or delegate |
| librarian | Cannot write, edit, or delegate |
| explore | Cannot write, edit, or delegate |
| multimodal-looker | Allowlist: `read` only |
| atlas | Cannot delegate |
| momus | Cannot write, edit, or delegate |

## Background Agents

Run agents in parallel. Up to 5 concurrent per model/provider. Circuit breaker support. Each background agent gets its own pane when tmux is enabled.

## Category System

Categories are agent configuration presets optimized for domains. When delegating, agents pick a category (not a model name). Categories map to models and settings automatically.

| Category | Default Model | Use Cases |
|-----------|--------------|-----------|
| visual-engineering | Gemini 3.1 Pro (high) | Frontend, UI/UX, design |
| ultrabrain | GPT-5.4 (xhigh) | Deep reasoning, architecture |
| deep | GPT-5.4 (medium) | Autonomous research + execution |
| artistry | Gemini 3.1 Pro (high) | Creative/artistic tasks |
| quick | GPT-5.4 Mini | Single-file changes, typos |
| unspecified-low | Claude Sonnet 4.6 | Low-effort general work |
| unspecified-high | Claude Opus 4.7 (max) | High-effort general work |
| writing | Gemini 3 Flash | Documentation, prose |

Custom categories supported via config with model, temperature, thinking, prompt_append, tool restrictions.

## Skills

Skills inject specialized knowledge and tools. Each skill has a trigger and carries its own MCP servers.

Built-in: `git-master` (3 specializations: Commit Architect, Rebase Surgeon, History Archaeologist), `playwright` (browser automation), `frontend-ui-ux` (design-first UI), `review-work` (5-agent parallel review), `ai-slop-remover` (de-AI humanize).

Skills load from `.opencode/skills/*/SKILL.md` or `~/.config/opencode/skills/*/SKILL.md` (priority: project → user). Custom skills supported via SKILL.md with embedded MCP definitions.

## 7 Commands

`/init-deep` (hierarchical AGENTS.md generation), `/ralph-loop` (self-referential dev loop), `/ulw-loop` (ultrawork + ralph), `/cancel-ralph`, `/refactor` (LSP+AST+TDD), `/start-work`, `/stop-continuation`, `/handoff`

## 52 Hooks

Organized into 5 tiers: Session (24 hooks), Tool-Guard (14), Transform (5), Continuation (7), Skill (2).

Key hooks include: IntentGate classification, keyword detection (ultrawork/search/analyze), think mode auto-detection, ralph loop management, todo continuation enforcement, comment checking (AI slop removal), hashline read/edit enhancement, context injection (AGENTS.md, README.md), compaction preservation, session recovery from API errors, model fallback chains, interactive bash session management.

## Hash-Anchored Edit Tool (Hashline)

Every Read output is tagged with `LINE#ID` content hashes. Edits validate hashes before applying. On mismatch, the edit is rejected. This eliminates stale-line errors entirely. Grok Code Fast 1 went from 6.7% to 68.3% success rate with this change alone.

## Session Recovery

Automatic recovery from: missing tool results, thinking block violations, empty messages, context window limits, JSON parse errors. Transparent to the user.

## Task System

File-based task persistence with dependency tracking. Tasks support `blockedBy` and `blocks` relationships. Stored as JSON in `.sisyphus/tasks/`. Differs from TodoWrite: persists across sessions, supports dependencies, enables automatic parallel execution.