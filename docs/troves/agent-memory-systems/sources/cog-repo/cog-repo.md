---
source-id: "cog-repo"
title: "Cog — Cognitive Architecture for Claude Code"
type: repository
url: "https://github.com/marciopuga/cog"
fetched: 2026-03-25T00:00:00Z
hash: "--"
highlights:
  - "CLAUDE.md"
  - "README.md"
  - ".claude/commands/reflect.md"
  - ".claude/commands/housekeeping.md"
  - ".claude/commands/evolve.md"
  - ".claude/commands/foresight.md"
  - ".claude/commands/scenario.md"
  - ".claude/commands/setup.md"
  - "memory/domains.yml"
selective: false
---

# Cog — Cognitive Architecture for Claude Code

A plain-text cognitive architecture for Claude Code that gives it persistent memory, self-reflection, and foresight. Created by Marcio Puga (MIT licensed, 2026).

## Overview

Cog is a set of conventions — not code — that teach Claude Code how to build and maintain its own memory. Everything lives in plain text (markdown + YAML). The filesystem is the interface. There is no server, no runtime, no application code.

## Architecture

### Three-Tier Memory

- **Hot** (`*/hot-memory.md`) — loaded every conversation, <50 lines each, rewrite freely
- **Warm** (domain files) — loaded when skill activates, per-file size limits
- **Glacier** (`memory/glacier/`) — YAML-frontmattered archives, indexed via `glacier/index.md`

### Progressive Condensation

`observations.md` (append) → `patterns.md` (distill 3+ on same theme) → `hot-memory.md` (rewrite freely)

Old observations (>50) → `glacier/` (indexed, retrievable)

### L0/L1/L2 Tiered Loading

Every memory file has a one-line `<!-- L0: ... -->` summary. Three retrieval tiers:
- L0 — one-line summary (decides whether to open)
- L1 — section header scan (identifies which part to read)
- L2 — full file read (when full context needed)

### Single Source of Truth (SSOT)

Each fact lives in ONE canonical file. Other files reference via `[[wiki-links]]`.

### Threads (Zettelkasten Layer)

Read-optimized synthesis files for recurring topics. Spine: Current State / Timeline / Insights. One file per topic, grows forever, never condensed.

### Domain Registry

Domains defined in `memory/domains.yml`. Types: personal, work, side-project, system. Created via conversational `/setup` command.

## Skills / Pipeline

| Skill | Purpose |
|-------|---------|
| `/setup` | Conversational domain bootstrapping |
| `/personal` | Personal life domain routing |
| `/reflect` | Mine conversations, extract patterns, condense observations, detect threads |
| `/evolve` | Audit memory architecture, propose rule changes (meta-level) |
| `/foresight` | Cross-domain strategic nudge (one nudge per run) |
| `/scenario` | Decision simulation with branch modeling and timeline overlay |
| `/housekeeping` | Archive, prune, link audit, glacier index, briefing bridge |
| `/history` | Deep multi-file memory search |
| `/explainer` | Writing (Atkins clarity + Montaigne inquiry) |
| `/humanizer` | Remove AI patterns from text (based on Wikipedia's AI Cleanup guide) |
| `/commit` | Git commit workflow |

### Pipeline Architecture

```
/housekeeping → briefing-bridge.md → /foresight → nudge
/reflect → patterns.md, self-observations.md
/evolve → rule changes (reads outputs of housekeeping + reflect)
/foresight → scenario candidates → /scenario
```

## Key Design Decisions

1. **Plain text over databases** — uses `grep`, `find`, `git diff` for observability
2. **Conventions over code** — CLAUDE.md + skill files define all behavior
3. **Interface-agnostic** — works in Claude Code CLI, Cowork, any Claude-powered tool
4. **MCP-extensible** — connecting calendar, email, Slack etc. makes memory actionable
5. **Self-improving** — `/evolve` audits and updates the rules themselves
6. **File boundaries between pipeline stages** — reflect/housekeeping/evolve/foresight have strict read/write scopes

## Influence / Research

Built on: RLM (recursive memory hierarchy), A-MEM (bi-directional back-linking), OpenViking (L0/L1/L2 tiered context), Zep/Graphiti (temporal validity), Mem0 (contradiction detection), Zettelkasten (thread framework), SSOT principles.

## Repository Structure

```
.claude/
  commands/         — skill files (markdown instructions)
    _templates/     — domain skill template
  settings.json     — Claude Code permissions
memory/
  domains.yml       — domain manifest (SSOT)
  hot-memory.md     — cross-domain hot memory
  link-index.md     — auto-generated backlink index
  cog-meta/         — self-improvement subsystem
  personal/         — personal domain
  glacier/          — archived data
CLAUDE.md           — conventions and rules
README.md           — documentation
```
