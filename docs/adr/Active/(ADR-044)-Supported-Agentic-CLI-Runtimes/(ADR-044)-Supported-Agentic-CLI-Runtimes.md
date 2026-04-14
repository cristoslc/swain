---
title: "Supported Agentic CLI Runtimes"
artifact: ADR-044
track: standing
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
supersedes: ADR-017
linked-artifacts:
  - EPIC-045
  - SPEC-175
depends-on-artifacts: []
evidence-pool: ""
---

# Supported Agentic CLI Runtimes

## Context

[ADR-017](../../Superseded/(ADR-017)-Supported-Agentic-CLI-Runtimes/(ADR-017)-Supported-Agentic-CLI-Runtimes.md)
established the initial supported runtime list (Claude Code, Gemini CLI, Codex CLI,
Copilot CLI, Crush). Three changes motivated a revision:

1. **opencode added.** `bin/swain` gained opencode support (`bbd0e573`). opencode is a
   distinct tool from Crush (which was previously named opencode before a rebrand). It
   uses a headless → TUI session-chaining pattern: `opencode run --format json` delivers
   the initial prompt and emits a session ID in its first JSON event; the TUI then resumes
   that session via `opencode --session <id>`. This gives opencode Full-tier capability
   without requiring a native interactive-prompt flag.

2. **Crush dropped.** Crush (the Partial-tier runtime, formerly named opencode) has not
   been tested in practice since the ADR-017 baseline. With opencode now covering the same
   use case at Full tier, carrying Crush as a Partial-tier option adds maintenance surface
   with no benefit.

3. **Gemini CLI dropped.** Gemini CLI's AGENTS.md ingestion depends on a `context.fileName`
   configuration entry that varies across versions and has not been validated against recent
   Gemini CLI releases. The maintenance cost of tracking Gemini flag changes outweighs its
   current usage.

## Decision

Swain officially supports the following agentic CLI runtimes:

| Runtime | Binary | Support tier | Notes |
|---------|--------|-------------|-------|
| **Claude Code** | `claude` | Full | Primary development runtime. Native AGENTS.md, `--dangerously-skip-permissions`, positional prompt. |
| **Codex CLI** | `codex` | Full | `--full-auto` for permission bypass, positional prompt. Native AGENTS.md. |
| **GitHub Copilot CLI** | `copilot` | Full | `--yolo` for permission bypass, `-i` for interactive+prompt. Native AGENTS.md. |
| **opencode** | `opencode` | Full | `--dangerously-skip-permissions` for permission bypass. Initial prompt delivered via `opencode run --format json`; session ID captured from first JSON event; TUI resumed via `opencode --session <id>`. |

### Support tiers

- **Full:** The launcher can deliver an initial prompt (`/swain-init` or equivalent) at
  session start. Fully autonomous operation is available.
- **Partial:** Interactive mode works but cannot accept an initial prompt. Reserved for
  future runtimes that meet the inclusion criteria but lack prompt-passing support.

### Adding new runtimes

A runtime qualifies for inclusion when it meets all of:

1. Has a terminal-based interactive mode (not just a web UI or PR-based agent).
2. Reads AGENTS.md natively or via a stable, version-independent configuration.
3. Supports some form of permission bypass for autonomous operation.
4. Works inside tmux.
5. Supports initial prompt delivery, either via a CLI flag or a stable programmatic
   handoff (such as the opencode JSON-event session-chain pattern).

File a spike to research the invocation pattern, then update this ADR and add launcher
templates. The `--dry-run` flag on `bin/swain` must be exercised against the new runtime
before merging.

### Dropped runtimes

| Runtime | Binary | Reason |
|---------|--------|--------|
| Gemini CLI | `gemini` | AGENTS.md ingestion unstable across versions; untested in practice. |
| Crush | `crush` | Partial-tier only; superseded by opencode for the same use case. |

Dropped runtimes are removed from `resolve_runtime` in `bin/swain`. If a user has a
dropped runtime installed, `bin/swain` will fall through to the next supported runtime
rather than launching a degraded session.

## Alternatives Considered

**Keep Gemini at Full tier, mark as untested.** Rejected — an "untested" entry in an
authoritative ADR creates false confidence and maintenance debt without adding value.

**Keep Crush as Partial tier.** Rejected — opencode covers the same use case at Full
tier. Two entries for effectively the same tool family serves no one.

**Promote opencode to Partial tier only.** The headless → TUI session-chain pattern
delivers the initial prompt reliably (session ID sourced from the first JSON event of the
headless run, not from a shared session list). This qualifies for Full tier.

## Consequences

**Positive:**
- Supported runtime list reflects what is actively tested and maintained.
- opencode at Full tier means `/swain-init` is delivered on session start, consistent
  with Claude Code behavior.
- Smaller runtime matrix reduces template maintenance surface.

**Accepted downsides:**
- Users who prefer Gemini CLI or Crush lose official support. They can still use those
  runtimes but will not get launcher templates or onboarding recommendations.
- opencode's headless → TUI chain adds one pre-launch step (the headless run) that other
  runtimes do not need. This is visible in `bin/swain` as a runtime-specific block in
  `phase3_launch_runtime`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Supersedes ADR-017; adds opencode, drops Gemini and Crush |
