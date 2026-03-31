# Synthesis: Claude Code Source Leak (2026-03-31)

## Overview

On March 31, 2026, a build configuration oversight shipped a source map file (cli.js.map) in the @anthropic-ai/claude-code@2.1.88 npm package. The 59.8 MB file contained the full original TypeScript source, revealing unreleased feature flags and internal development directions. This trove captures the community analysis of that leak.

## Key Findings

### Autonomous Agent Architecture

Three feature flags point toward Claude Code becoming a persistent, autonomous agent:

- **KAIROS** (154 references) — daemon mode with background sessions, "dream" memory consolidation, GitHub webhook subscriptions, push notifications, and channel-based communication
- **PROACTIVE** (37 references) — independent work between user messages via "tick" prompts; the model decides what to do on each wake-up
- **COORDINATOR_MODE** (32 references) — orchestrator pattern that spawns and manages parallel worker agents for research, implementation, and verification

This is directly relevant to swain's architecture. KAIROS's "dream" memory consolidation parallels swain's trove system. COORDINATOR_MODE maps closely to swain's subagent dispatching patterns. The "tick" prompt mechanism in PROACTIVE mode is a platform-level version of what swain's session management does manually.

### Permission Automation

**TRANSCRIPT_CLASSIFIER** (107 references) — an AI classifier to auto-approve tool permissions. This would reduce or eliminate the approval prompts that currently interrupt agentic workflows. Swain already works around this friction with permission presets and trusted tool configurations.

### Internal Model Landscape

- **Capybara** — Claude 4.6 variant; "v8" had a 29-30% false claims rate (vs v4's 16.7%), over-commenting tendency, and an "assertiveness counterweight"
- **Fennec** — codename migrated to Opus 4.6
- **Numbat** — unreleased model ("Remove this section when we launch numbat")
- **opus-4-7 / sonnet-4-8** — referenced as version numbers that should never appear in public commits, implying internal existence

### Stealth Contribution System

**Undercover Mode** strips AI attribution from commits when Anthropic employees contribute to public repos. No force-OFF switch — defaults to on outside internal repos. This has implications for open-source provenance and transparency.

### Additional Signals

- **VOICE_MODE** (46 refs) — speech-to-text and text-to-speech integration
- **BUDDY** — Tamagotchi-style terminal pet system with 18 species, rarity tiers, cosmetics, and stats
- **FORK_SUBAGENT** — parallel agent forking
- **VERIFICATION_AGENT** — adversarial verification of work
- **ULTRAPLAN** — advanced planning capabilities
- **TOKEN_BUDGET** — explicit token budget targeting ("+500k", "spend 2M tokens")
- **TEAMMEM** — team memory sync across users

## Relevance to Swain

| Leaked Feature | Swain Analog | Implication |
|---|---|---|
| KAIROS daemon mode | swain-session lifecycle | Platform may absorb session persistence; swain should prepare to integrate or layer on top |
| COORDINATOR_MODE | subagent-driven-development | Platform orchestration could replace or complement swain's dispatch patterns |
| TRANSCRIPT_CLASSIFIER | Permission presets in AGENTS.md | If auto-approve ships, swain's permission workarounds become less critical |
| TEAMMEM | Memory system (MEMORY.md) | Team memory sync could change how swain's per-project memory works |
| VERIFICATION_AGENT | verification-before-completion skill | Platform-level verification could augment or replace the skill |
| TOKEN_BUDGET | No direct analog | New resource management primitive swain could leverage |

## Gaps

- No details on KAIROS's scheduling mechanism (cron-like? event-driven? both?)
- No clarity on whether COORDINATOR_MODE workers share context or are fully isolated
- Unknown timeline for any of these features reaching GA
- The article is one person's analysis of decompiled source — feature flags may be experimental or abandoned
