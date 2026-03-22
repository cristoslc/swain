---
title: "Cross-Runtime Portability Substrate"
artifact: SPIKE-029
track: container
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "What extension models do non-Claude agent runtimes (opencode, gemini cli, codex, copilot, aider) support, and is there a common substrate that swain could target for cross-runtime portability?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Building per-runtime adapters that share no common foundation
  - Targeting runtimes with unstable or nonexistent extension APIs
evidence-pool: ""
linked-artifacts:
  - EPIC-032
  - EPIC-033
  - SPIKE-028
---

# Cross-Runtime Portability Substrate

## Summary

**Go.** Two shared substrate layers cover 6+ runtimes: AGENTS.md (universal instruction layer, Linux Foundation-governed, 60K+ repos) and MCP (universal tool layer, supported by every major runtime except Aider). A third layer — SKILL.md in `.agents/skills/` — is emerging as a cross-runtime skill discovery convention supported by OpenCode, Gemini CLI, Cursor, and Copilot. Swain's existing packaging conventions are already compatible with the emerging standards.

## Question

What extension models do non-Claude agent runtimes (opencode, gemini cli, codex, copilot, aider) support, and is there a common substrate that swain could target for cross-runtime portability?

## Go / No-Go Criteria

- **Go**: At least 2 non-Claude runtimes support a shared extension mechanism (AGENTS.md, MCP, tool plugins, or system prompt injection) that swain could target with a single adapter
- **No-Go**: Every runtime has a completely bespoke extension model with no overlap, making cross-runtime portability a per-runtime maintenance burden

## Pivot Recommendation

If no common substrate exists, deprioritize cross-runtime portability in favor of Claude-surface-only packaging (SPIKE-028) and revisit when the ecosystem matures. Consider publishing swain's patterns as a specification/protocol rather than runnable code.

## Findings

Evidence pools: agent-runtime-extensions, portable-framework-patterns (troves archived)

### Three Shared Substrate Layers

**Layer 1: AGENTS.md (instruction/context layer)**
- Linux Foundation AAIF-governed standard since December 2025
- Native auto-discovery in: Codex CLI, OpenCode, Cursor, Windsurf, Copilot, Gemini CLI (configured), VS Code
- 60K+ repo adoption
- Plain markdown, no schema required — swain's AGENTS.md works as-is
- Notable: Claude Code is the holdout (uses CLAUDE.md). OpenCode bridges by reading both.
- Swain's `CLAUDE.md @AGENTS.md` pattern is confirmed best practice

**Layer 2: MCP (tool/action layer)**
- Supported natively by: Codex CLI, OpenCode, Gemini CLI, Copilot CLI, Cursor, Windsurf, VS Code, JetBrains IDEs, Zed, Continue.dev, Replit
- Not supported: Aider (community workarounds only)
- One MCP server works across all compliant hosts
- A swain MCP server would be instantly available in 10+ clients

**Layer 3: SKILL.md in `.agents/skills/` (skill discovery)**
- OpenCode: discovers `.agents/skills/` and `.opencode/skills/` paths, loads SKILL.md on demand
- Gemini CLI: discovers `.agents/skills/` (prioritized over `.gemini/skills/`), full skill consent flow
- Cursor: supports SKILL.md as "domain-specific knowledge packages"
- Copilot: skill files work across CLI, coding agent, and VS Code
- Swain already installs to `.agents/skills/` — zero work needed for discovery

### Runtime-by-Runtime Compatibility

| Runtime | AGENTS.md | MCP | SKILL.md | Swain Readiness |
|---------|-----------|-----|----------|----------------|
| Claude Code | Via CLAUDE.md | Full | Full | Current home — works |
| OpenCode | Native + CLAUDE.md fallback | Full | `.agents/skills/` | Ready now — zero changes |
| Gemini CLI | Configured | Full | `.agents/skills/` | Ready now — zero changes |
| Codex CLI | Native (originator) | Full | Documented | Ready now — AGENTS.md works |
| Copilot CLI | Native | Full | Skill files | Ready now — AGENTS.md works |
| Cursor | Native | Full | Supported | Ready now — AGENTS.md works |
| Windsurf | Native | Full | Via rules | Ready now — AGENTS.md works |
| VS Code | Via Copilot | Full | Via Copilot | Ready now — AGENTS.md works |
| Aider | Manual config | Community only | No | Low priority — manual effort |

### What Degrades Across Runtimes

Swain's full capability requires Claude Code-specific features that don't exist elsewhere:
- **Skill chaining** (swain-design → brainstorming → writing-plans) — Claude Code only
- **Session startup auto-invocation** (swain-doctor → swain-session) — Claude Code only
- **Hook-based automation** (PostToolUse, Stop events) — Claude Code only
- **Model-per-skill overrides** (YAML frontmatter `model:`) — Claude Code only
- **Tool permission scoping** (`allowed-tools` in frontmatter) — Claude Code only

What works everywhere:
- AGENTS.md governance rules and routing tables
- SKILL.md instructions as plain context (degraded but useful)
- MCP server tools (artifact queries, status, transitions)
- Artifact model (markdown files in docs/) — always readable

### Key Insight: The Bundle Model Is Converging

Gemini CLI extensions (MCP + context file + commands), Copilot plugins (MCP + agents + skills + hooks), and Claude Code plugins (MCP + skills + hooks) all describe the same pattern: **a distributable unit that bundles context, tools, and behavior**. Swain's skill model is architecturally compatible. The opportunity is to produce one source tree that generates per-platform bundles.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
| Complete | 2026-03-18 | | Research complete, findings documented |
