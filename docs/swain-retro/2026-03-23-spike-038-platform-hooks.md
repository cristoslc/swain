---
title: "Retro: SPIKE-038 Platform Hooks Validation"
artifact: RETRO-2026-03-23-spike-038-platform-hooks
track: standing
status: Active
created: 2026-03-23
last-updated: 2026-03-23
scope: "SPIKE-038 research and validation session — trove creation, vision/initiative decomposition, live testing across 4 platforms"
period: "2026-03-22 — 2026-03-23"
linked-artifacts:
  - SPIKE-038
  - VISION-005
  - INITIATIVE-020
  - SPIKE-039
  - SPIKE-040
  - SPIKE-041
---

# Retro: SPIKE-038 Platform Hooks Validation

## Summary

Created trove `platform-hooks-validation` (5 sources across Claude Code, Gemini CLI, Codex CLI, Copilot CLI, OpenCode), stood up VISION-005 (Trustworthy Agent Governance) with INITIATIVE-020 (Platform Enforcement Substrate) and 4 research spikes, then validated SPIKE-038 (PreToolUse Hook Adapter Feasibility) by live-testing hook prototypes on 4 platforms. Result: Go on 4/5 platforms with committed prototypes.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| Trove `platform-hooks-validation` | Platform hooks and validation mechanisms | Created (5 sources) |
| VISION-005 | Trustworthy Agent Governance | Created (Active) |
| INITIATIVE-020 | Platform Enforcement Substrate | Created (Proposed), findings written back |
| SPIKE-038 | PreToolUse Hook Adapter Feasibility | Complete (Go: 4/5) |
| SPIKE-039 | MCP Session-State Tracker Design | Created (Proposed) |
| SPIKE-040 | Post-Hoc Process Audit Pipeline | Created (Proposed) |
| SPIKE-041 | Cross-Platform Deny-Rule Portability | Created (Proposed) |
| `swain-dispatch` | Deprecated | Requires API billing |

## Reflection

### What went well

**Parallel research agents per platform.** Launching 5 research agents simultaneously (one per platform) cut what would have been ~20 minutes of serial web research into ~5 minutes. Each agent returned comprehensive, source-cited findings. This pattern should be repeated for any multi-platform or multi-source research task.

**Trove-first, then artifacts.** Building the trove before creating VISION-005, INITIATIVE-020, and the spikes meant every artifact had an evidence base from day zero. The hierarchy was grounded in research, not speculation. The trove's synthesis directly informed the spike's Go/No-Go criteria and the initiative's track structure.

### What was surprising

Nothing — the session ran smoothly without unexpected blockers.

### What would change

Nothing about the approach. The research → artifacts → validation pipeline worked well.

### Patterns observed

**Foreign runtime testing via agents is effective but brittle.** Using Claude Code agents to install hooks, run test prompts, and report results on Gemini CLI, Copilot CLI, and OpenCode produced valid Go/No-Go answers. However, the evidence chain is indirect:

- We trust the agent's report, not a reproducible test script
- The Copilot agent built a 9-test harness inline that isn't easily re-runnable
- The OpenCode agent discovered a trove error (hook signature is `(input, output)` not `(input)`) only because it hit runtime errors — a different agent run might miss this
- The Gemini deny test timed out, which we correctly interpreted as "hook blocked," but a proper test would assert on structured output

**Mitigation needed:** Each platform's hook prototype should have a companion deterministic test script (e.g., `scripts/test-hooks/<platform>-test.sh`) that can be re-run without an agent. The spike produced prototypes but not repeatable test harnesses.

## Learnings to encode in skills

Behavioral changes belong in skills, not memory (per ADR convention). These learnings need skill updates:

| Learning | Target skill | Change needed |
|----------|-------------|---------------|
| Parallel agents per platform for multi-source research | `swain-search` | Add guidance to launch parallel agents when 3+ sources/platforms are involved |
| Build trove before creating artifacts — evidence base from day zero | `swain-search` / `swain-design` | Strengthen trove-first ordering in the research → artifact pipeline |
| Agent-mediated foreign runtime testing needs companion test scripts | `swain-design` or new skill | When spikes test foreign runtimes, require committed test harnesses alongside prototypes |
