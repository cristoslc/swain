---
title: "Retro: SPEC-297 Session Purpose Text Drop"
artifact: RETRO-2026-04-13-spec-297-session-purpose-drop
track: standing
status: Active
created: 2026-04-13
last-updated: 2026-04-13
scope: "Fix session purpose text being dropped during swain-init startup"
period: "2026-04-13 — 2026-04-13"
linked-artifacts:
  - SPEC-297
---

# Retro: SPEC-297 Session Purpose Text Drop

## Summary

Moved session-purpose handling from agent-dependent skill instructions into deterministic code in the greeting pipeline. Previously, `swain-init/SKILL.md` and `swain-session/SKILL.md` told agents to parse `Session purpose: <text>` from the prompt and call `swain-bookmark.sh`, which was unreliable across runtimes. The fix: the launcher always exports `SWAIN_PURPOSE`, the greeting script reads it and writes the bookmark deterministically, and the agent just displays the value from the greeting JSON.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-297 | Fix swain-init Session Purpose Text Drop | Complete |

## Reflection

### What went well

The TDD cycle (RED → GREEN → refactor) caught edge cases early. Writing the failing test first revealed three distinct failure modes (bookmark not written, JSON field missing, human output missing) that would have been missed with a single assertion. The five-task decomposition was crisp: each task had a clear input, output, and done condition.

The env-var approach (`SWAIN_PURPOSE`) was the right abstraction. It decouples the launcher (which knows the purpose text) from the greeting script (which consumes it), making the contract explicit and testable without mocking agent behavior.

### What was surprising

The bug was subtle: the purpose text worked for the crush runtime (which already exported `SWAIN_PURPOSE`) but was silently dropped for Claude, Gemini, Codex, and Copilot runtimes. The existing code had a two-class system for runtimes that was not documented anywhere.

### What would change

The skill instructions should have been audited for agent-dependent behavior earlier. The pattern of telling an agent to parse natural language and call a script is fragile — this is the same class of problem that ADR-018 (runtime invocations must be structural, not prosaic) addressed for launchers, but the principle was not applied to the greeting pipeline.

### Patterns observed

This is a recurring theme: swain has shifted from agent-dependent instructions to deterministic scripts multiple times (session bootstrap consolidation in SPEC-172, preflight self-healing in SPEC-191, deprecating swain-session in SPEC-172). Each time, the root cause was the same — asking agents to do work that a script can do reliably. The env-var + JSON output pattern (launcher sets env var, script reads it and surfaces in structured JSON, agent displays from JSON) is emerging as a general pattern for agent-script handoffs.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Agent-script handoff pattern | SPEC candidate | Generalize the `SWAIN_*` env-var → script → JSON pattern as a convention: launcher exports env vars, scripts read them and produce structured JSON, agents render from JSON. This replaces asking agents to parse prose and call scripts. |
| Runtime parity testing | SPEC candidate | Add a test harness that verifies all Tier-1 launcher templates export the same env vars. The crush-only `SWAIN_PURPOSE` export was an undetected drift. |
| Worktree symlink gap | issue | Worktrees created without `.agents/skills/` and `.claude/skills/` symlinks, breaking skill access. The `.agents/skills/` and `.claude/skills/` symlinks had to be created manually in this worktree. |

## SPEC candidates

1. **Agent-script handoff convention** — Generalize the `SWAIN_*` env-var → script → JSON pattern as an ADR or convention. Launcher always exports structured env vars; scripts read them, act deterministically, and surface results in JSON; agents render from JSON fields only. This replaces fragile "agent parses prompt and calls script" instructions across all skills.

2. **Runtime parity CI** — Add a test or CI check that all Tier-1 launcher templates export the same set of `SWAIN_*` env vars. Prevent the crush-only drift that caused this bug from recurring.