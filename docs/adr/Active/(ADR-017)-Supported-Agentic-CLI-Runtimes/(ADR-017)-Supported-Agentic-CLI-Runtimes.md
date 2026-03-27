---
title: "Supported Agentic CLI Runtimes"
artifact: ADR-017
track: standing
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
linked-artifacts:
  - SPIKE-047
  - EPIC-045
  - SPEC-172
depends-on-artifacts: []
evidence-pool: ""
---

# Supported Agentic CLI Runtimes

## Context

Swain's shell launcher templates (EPIC-045) originally hardcoded Claude Code as the only agentic runtime. However, swain's vision (VISION-003, "Swain Everywhere") calls for portability across agent surfaces. Multiple agentic CLI tools now exist that read AGENTS.md, support permission bypass for autonomous operation, and can accept initial prompts — making them viable swain runtimes.

SPIKE-047 researched the invocation patterns of five candidate runtimes and found all are compatible with swain's launcher pattern to varying degrees.

## Decision

Swain officially supports the following agentic CLI runtimes for shell launcher templates and onboarding recommendations:

| Runtime | Binary | Support tier | Notes |
|---------|--------|-------------|-------|
| **Claude Code** | `claude` | Full | Primary development runtime. Native AGENTS.md, `--dangerously-skip-permissions`, positional prompt. |
| **Gemini CLI** | `gemini` | Full | `-y` for permission bypass, `-i` for interactive+prompt. Reads AGENTS.md via `context.fileName` config. |
| **Codex CLI** | `codex` | Full | `--full-auto` or `--yolo` for permission bypass, positional prompt. Native AGENTS.md. |
| **GitHub Copilot CLI** | `copilot` | Full | `--yolo` for permission bypass, `-i` for interactive+prompt. Native AGENTS.md. |
| **Crush** (formerly opencode) | `crush` | Partial | `--yolo` for interactive permission bypass. No interactive+prompt mode — see notes below. Native AGENTS.md. |

### Support tiers

- **Full:** Interactive mode accepts an initial prompt. Launcher template can pass `/swain-init` (or equivalent) on startup. Fully autonomous operation available.
- **Partial:** Interactive mode works but cannot accept an initial prompt. Launcher starts the runtime bare; session initialization depends on AGENTS.md auto-invoke directives or runtime-specific startup hooks.

### Adding new runtimes

A runtime qualifies for inclusion when it meets all of:
1. Has a terminal-based interactive mode (not just a web UI or PR-based agent)
2. Reads AGENTS.md (natively or via configuration)
3. Supports some form of permission bypass for autonomous operation
4. Works inside tmux

File a spike to research the invocation pattern, then update this ADR and add launcher templates.

## Alternatives Considered

**Claude Code only.** Simplest path, but conflicts with VISION-003's portability goal. Users who prefer other runtimes would get no onboarding support.

**Support everything with a CLI.** Too broad — runtimes that can't read AGENTS.md or accept initial prompts provide a degraded experience that creates support burden without proportional value.

**Runtime-agnostic wrapper script.** A single `swain` binary that detects which runtimes are installed and delegates. Rejected as premature — the template-per-runtime approach is simpler, inspectable, and sufficient for now. A wrapper could be a future enhancement if the runtime list grows beyond what templates can manage.

## Consequences

**Positive:**
- Shell launcher templates cover the five major agentic CLI tools as of 2026-03
- Template directory structure must accommodate multiple runtimes (addressed by SPEC-172)
- swain-init can recommend the runtime the user already has installed
- Users can switch runtimes without losing swain's onboarding experience

**Accepted downsides:**
- Template maintenance scales linearly with `runtimes x shells` — currently 5x3 = 15 files (or fewer with a smarter structure)
- Crush has partial support due to no interactive+prompt mode — may improve as Crush evolves
- CLI flag interfaces may change across runtime versions — templates must be version-aware or accept breakage risk
- Each new runtime requires a research spike before inclusion

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation, informed by SPIKE-047 |
