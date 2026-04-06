---
title: "Swain Runtime Adapter Architecture"
artifact: SPIKE-061
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "Should swain present a Claude Code plugin shape to Claude Code while conforming to the Agent Skills standard for other runtimes — and if so, how deep should the adapter layer go?"
gate: Pre-MVP
risks-addressed:
  - Swain is tightly coupled to Claude Code conventions, limiting portability.
  - The Agent Skills ecosystem is converging on a standard that swain partially diverges from.
  - Claude Code's plugin system offers features (namespacing, bin/ PATH, hooks) swain reinvents.
linked-artifacts:
  - ADR-036
  - EPIC-068
  - INITIATIVE-002
depends-on-artifacts: []
trove: agent-script-directory-conventions
---

# Swain Runtime Adapter Architecture

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Should swain detect its host runtime and present different "shapes" to different agents? Three options on the table:

**Option A — Status quo.** Swain installs into `.claude/skills/` and `.agents/` with its own conventions. Works on Claude Code. Other runtimes get partial support via `.agents/skills/` (the cross-tool standard path). No plugin manifest, no host-specific adaptation.

**Option B — Claude plugin + status quo for others.** Swain generates a `.claude-plugin/plugin.json` manifest during init, making it a first-class Claude Code plugin. It gains namespaced skills (`/swain:design`), a `bin/` directory on the Bash tool's PATH, hook integration, and marketplace distribution. Other runtimes continue using `.agents/skills/` as today.

**Option C — Full hexagonal.** Swain's core (artifacts, lifecycle, governance, scripts) is runtime-agnostic. A port/adapter layer detects the host and generates the right shape: Claude Code plugin, Codex `.agents/` layout, OpenCode multi-path, Kiro `.kiro/skills/`, Goose conventions, etc. `npx swain-init` runs the detection and wires the adapter. When a host adopts a new plugin system, swain adds an adapter without touching core.

## Go / No-Go Criteria

| Criterion | Measure | Pass threshold |
|-----------|---------|---------------|
| Runtime coverage | How many of the top 5 agentic runtimes (Claude Code, Codex, OpenCode, Cursor, Kiro) can swain support with each option? | Option must cover ≥3 runtimes with working skill discovery. |
| Migration cost | Lines of code + skill files changed to adopt the option. | ≤500 LOC for Option B; ≤2000 LOC for Option C. If higher, the option is too expensive for current project scale. |
| Claude Code plugin value | Does presenting as a native plugin unlock features swain currently reinvents? | Must unlock ≥2 of: namespace collision prevention, `bin/` PATH injection, hook registration, marketplace distribution. |
| Adapter complexity | For Option C, how many host-specific behaviors exist beyond skill path routing? | If ≤3 host-specific behaviors, the adapter layer is over-engineering. If ≥6, it justifies the abstraction. |
| Ecosystem trajectory | Are other runtimes converging toward a single standard or diverging? | If converging (Agent Skills standard winning), Option B suffices. If diverging, Option C has stronger justification. |

## Pivot Recommendation

If the spike finds that host-specific behaviors are minimal (≤3 beyond skill path routing), stay with **Option B** — Claude plugin shape for the primary runtime, bare Agent Skills standard for everything else. The hexagonal abstraction only pays for itself when there are enough distinct behaviors to justify the adapter interface.

If the spike finds Claude Code plugin features don't meaningfully improve swain's DX (e.g., namespace collision already solved by ADR-036, `bin/` PATH not useful), stay with **Option A** and revisit when the ecosystem stabilizes.

## Investigation threads

### Thread 1 — Claude Code plugin anatomy

What does swain gain by becoming a native plugin?

- Does `/swain:design` (namespaced skill invocation) improve over `/swain-design`?
- Does plugin `bin/` on PATH solve the operator DX problem for `swain` and `swain-box`?
- Can plugin `hooks/hooks.json` replace swain's current hook setup in `settings.json`?
- Does marketplace distribution (`/plugin install swain@marketplace`) replace `npx` install?
- What does swain lose? Plugin skills are namespaced — does that break existing `/swain-design` invocations?

### Thread 2 — Cross-runtime adapter surface

What actually differs between runtimes?

- Skill discovery paths (already known: `.claude/skills/`, `.agents/skills/`, `.kiro/skills/`, etc.).
- Script execution model (bash vs sandboxed vs approval-gated).
- Hook/event system (Claude hooks vs none).
- Memory/state conventions (`.claude/memory/` vs nothing).
- Session management (Claude session state vs none).

Catalog the delta. If it's just paths, the "adapter" is a symlink farm and Option B suffices.

### Thread 3 — Ecosystem trajectory

Where is the standard heading?

- Is AAIF converging the foundations toward one layout, or are runtimes diverging?
- Are other runtimes adopting plugin systems (Codex plugins? OpenCode plugins?)?
- What does Goose, Gemini CLI, and Cursor's agent mode look like?
- How fast is the ecosystem moving — will today's adapter be stale in 3 months?

### Thread 4 — Migration mechanics

For Option B, what does the init/doctor change look like?

- Can swain-init detect "am I running inside Claude Code?" and generate `plugin.json`?
- Can the same install serve both Claude Code (plugin shape) and other runtimes (bare skills)?
- Does the dual shape create confusion — two ways to invoke the same skill?

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created alongside EPIC-068 (ADR-036). Scoped to three options: status quo, Claude plugin hybrid, full hexagonal. |
