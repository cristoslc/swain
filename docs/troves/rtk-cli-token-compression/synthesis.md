# RTK CLI Token Compression — Synthesis

## Overview

RTK (Rust Token Killer) is an open-source CLI proxy that compresses command outputs before they reach an AI agent's context window. It intercepts 30+ standard shell commands (test runners, git, file operations, grep, find, ls, deps) and applies command-specific filters that strip boilerplate while preserving actionable information. Claims 89% average noise removal across 2,900+ measured commands.

## Key findings

### The problem is real and quantifiable
A typical 2-hour AI coding session runs ~60 CLI commands generating ~210K tokens of output. On a 200K-token context window, CLI noise alone can overflow the context. RTK reduces this to ~23K tokens. The compression ratios are command-specific: test runners compress 96-99% (stripping per-test PASS lines), git diff 94%, file reads 80-95% (skeleton mode), while grep is lower at 55%.

### Integration via hooks, not process wrapping
RTK installs itself as a Claude Code `PreToolUse` hook via `rtk init --global`. This means it transparently rewrites Bash commands to `rtk` equivalents. The agent never knows its outputs are being compressed — no agent-side configuration needed. This is the same hook mechanism that swain uses for validation and that the `ai-development-patterns` trove documents as the Event Automation pattern.

### Compression is lossy but structured
RTK doesn't just truncate. Each command type has a purpose-built filter:
- Test runners: summary + failures only (262 passing tests -> 1 line)
- Git diff: diffstat + key hunks (drops unchanged context lines)
- File read: structure declarations preserved, bodies elided
- Git log: one-line format, stats stripped

This is lossy — the agent can't see every passing test name or every unchanged context line. But for most agent workflows, the summary is sufficient. When it's not, the agent can re-run without RTK.

### Economic argument is tool-agnostic
RTK positions itself against every major AI coding tool's pricing/limits. The argument holds regardless of pricing model: flat-rate plans get longer sessions (3x), pay-per-token plans get lower costs (~70% reduction), credit-based plans stretch further (~2x). The common thread is that CLI output is the largest controllable source of token waste.

### Gain tracking creates a feedback loop
The `rtk gain` command reads from a local SQLite database to show cumulative savings per command type. This makes the value proposition self-reinforcing: the more you use it, the more impressive the stats, the less likely you are to uninstall it.

## Relevance to swain

### Direct applicability
Swain agents run many CLI commands (chart.sh, doctor, preflight, git operations, test runners). RTK could reduce context consumption during long sessions, especially for dispatched agents that hit context limits. The `PreToolUse` hook integration is the same mechanism swain already uses.

### Considerations before adoption
1. **Lossy compression risks** — If a swain agent needs full test output to diagnose a failure, RTK's summary may hide the relevant detail. The agent would need to re-run without compression, adding a round-trip.
2. **Hook stacking** — Swain already uses PreToolUse hooks for validation. RTK adds another hook to the chain. Need to verify they compose correctly.
3. **Selective compression** — Some swain commands (chart.sh output, specgraph JSON) should NOT be compressed — they're structured data the agent needs verbatim. RTK would need command-level exclusions.
4. **Filter levels** — RTK supports `aggressive` mode for file reads. The default vs. aggressive tradeoff needs testing per swain workflow.

### Adjacent trove connections
- **`ai-development-patterns`** — Event Automation pattern describes the same PreToolUse hook mechanism RTK uses for integration
- **`ai-development-patterns`** — Context Persistence pattern addresses the same "context is a finite resource" problem from the structured-files angle rather than the compression angle

## Gaps

1. **No failure-mode documentation** — What happens when compression strips information an agent actually needs? No documented recovery pattern.
2. **No per-directory or per-project config** — Hook is global (`--global`). No way to configure different compression levels for different projects.
3. **No integration testing with non-Claude agents** — Site focuses on Claude Code hooks. Unclear how it integrates with agents that don't use PreToolUse (opencode, gemini cli, codex).
4. **Cloud product is vaporware** — RTK Cloud (team analytics, $15/dev/month) is waitlist-only with "0 teams" shown. Evaluate the open-source CLI on its own merits.
5. **No structured output mode** — RTK outputs human-readable compressed text. No JSON or machine-readable format for agents that parse structured data.
