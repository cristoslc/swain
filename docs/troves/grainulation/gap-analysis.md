# Grainulation vs. Swain — Gap Analysis

**Date:** 2026-04-06
**Method:** Deep read of all 9 grainulation repos + swain source

---

## 1. Intended Purpose

**Grainulation** is a structured research toolkit that treats technical decisions like code in a CI/CD pipeline.

> Question → grow typed claims with confidence levels → challenge findings → compile a brief only when conflicts resolve.

Problem it solves: decision makers lack an auditable way to accumulate and validate technical evidence. Findings live in heads, can't be versioned, and have no conflict detection.

**Swain** is a decision-support and alignment system for solo developers delegating to AI coding agents.

> Decide what to build → agents implement → capture what happened → verify alignment.

Problem it solves: AI agents move fast but drift from decisions. Intent evaporates between sessions. Agents violate architectural constraints because reasoning isn't persistent.

---

## 2. Target Audience

| Dimension | Grainulation | Swain |
|---|---|---|
| Primary user | Solo researcher, anyone answering "should we?" | Solo developer delegating to AI agents |
| Team size | Solo or small team | Solo only (explicitly) |
| Use case | Technical decisions, evidence evaluation | Feature dev, bug fixes, refactoring with agent assistance |
| Agent role | Optional research assistant | Required execution layer |
| Entry point | A question to answer | A decision already made |

---

## 3. Core Architecture

### Grainulation: the Ecosystem Model

Nine independent tools, zero npm dependencies, all share `claims.json`.

| Tool | Role |
|---|---|
| **wheat** | Research engine — interactive sprints, 7-pass compiler, conflict detection. |
| **grainulator** | Claude Code plugin — 13 skills, autonomous subagent, demo PWA. |
| **farmer** | Remote permission dashboard — mobile + desktop, trust tiers. |
| **mill** | Export engine — 24 formats (PDF, CSV, Jira, GitHub, Obsidian, slides, SQL, TypeScript). |
| **silo** | Knowledge store — 11 pre-built claim packs, 131 curated claims. |
| **harvest** | Analytics — cross-sprint patterns, prediction scoring, knowledge decay, velocity. |
| **orchard** | Multi-sprint orchestrator — dependency graphs, conflict detection. |
| **barn** | Shared utilities (sprint detection, PDF builds, 17 HTML templates). |
| **grainulation** | Unified CLI entry point. |

Key principles: claim-driven everything. The 7-pass compiler blocks output if conflicts exist. Evidence tiers: `stated → web → documented → tested → production`.

### Swain: the Intent-Loop Model

Twelve integrated skills, git as the persistence layer, artifacts as single source of truth.

| Skill | Role |
|---|---|
| **swain-design** | Artifact creation and lifecycle (Vision → Initiative → Epic → Spec → ADR). |
| **swain-do** | Task tracking, implementation plans, worktree creation. |
| **swain-roadmap** | Status dashboard, what's-next recommendations. |
| **swain-search** | Source collection → normalized troves. |
| **swain-sync** | Fetch, rebase, commit, push with ADR compliance checking. |
| **swain-init / swain-teardown** | Session boundaries, focus lanes, cleanup. |
| **swain-doctor** | Health checks, auto-repair. |
| **swain-retro** | Learnings at EPIC closure. |
| **swain-release** | Changelog, version bump, git tag. |

Key principles: operator decides, agent executes, git audits. Worktree-isolated implementation. Phase-gated artifact lifecycle.

---

## 4. Feature Comparison

| Feature | Grainulation | Swain |
|---|---|---|
| Primary primitive | `claims.json` — typed, evidence-graded. | Markdown artifacts in `docs/`. |
| Validation model | 7-pass compiler **blocks** output on conflicts. | Phase gates + ADR compliance — surfaces divergence, operator resolves. |
| Evidence confidence | Explicit 5-level tiers. | Implicit (derived from source type). |
| Conflict detection | Hard block. | Drift detection — soft alert. |
| Agent integration | Claude Code plugin (grainulator) + MCP server. | Claude Code skills — agent-agnostic markdown context. |
| Remote approval UI | Farmer — mobile/desktop dashboard, trust tiers. | Built-in agent hooks (no external service). |
| Knowledge packs | Silo — 11 pre-built packs, 131 claims. | Troves — external source collections (no curated packs). |
| Export formats | Mill — 24 formats. | Native markdown only. |
| Cross-sprint analytics | Harvest — velocity, prediction calibration, decay. | Per-EPIC retros (no cross-epic analytics). |
| Multi-sprint coordination | Orchard — dependency graphs, team assignment. | Initiative hierarchy (no conflict detection across branches). |
| Adversarial testing | `/challenge` command built in. | Not present. |
| Work decomposition | Not enforced (flat sprints). | Core — Vision → Initiative → Epic → Spec. |
| Worktree isolation | Not present. | Core — ephemeral linked worktrees per implementation task. |
| Session management | Not explicit. | Explicit — `swain-init` / `swain-teardown`, SESSION-ROADMAP, focus lanes. |
| ADR compliance enforcement | Not present. | Pre-commit hook + sync-time check. |
| Autonomous agent sprints | Yes (grainulator subagent). | Intentional anti-pattern — operator supervises. |
| Readability enforcement | Not present. | Flesch-Kincaid grade ≤10 enforced on artifacts. |
| Predictive scoring | Harvest scores estimates vs. outcomes. | Not present. |
| Dependency model | Node built-ins only — zero deps. | git (required) + optional: gh, uv, jq, fswatch. |
| Offline capability | Yes. | Yes. |
| PWA/browser demo | grainulator.app with WebLLM inference. | CLI/agent only. |

---

## 5. Philosophical Differences

| Dimension | Grainulation | Swain |
|---|---|---|
| Decision model | Decisions **emerge** from compiled evidence. | Decisions are **human-made**; system captures and enforces them. |
| Validation philosophy | **Prevent** wrong output — block compilation. | **Detect** divergence — surface to operator, operator resolves. |
| Autonomy | Autonomous sprints possible via subagent. | Agents are always supervised; operator holds strategic judgment. |
| Time scope | Single sprint; Harvest looks cross-sprint. | Session → EPIC → retro; no cross-EPIC analytics. |
| Flexibility | High — opt-in modular, any tool standalone. | Medium — artifacts and phases are prescriptive. |
| Agent relationship | Research assistant (optional, can run unattended). | Mandatory execution layer (never unattended on strategy). |

---

## 6. Gaps

### What Swain has that Grainulation lacks

- Hierarchical work decomposition (Vision → Spec).
- Worktree-isolated implementation safety.
- ADR compliance enforcement at commit time.
- First-class artifact lifecycle phases (git-tracked subdirectory).
- Session management with focus lanes and resumption.
- User Journey and Persona artifact types.
- Prose readability enforcement (Flesch-Kincaid grade).
- Superpowers skill chaining (brainstorm → plan → TDD → verify).
- Operator sustainability model (finite attention as a design constraint).

### What Grainulation has that Swain lacks

- Explicit evidence tiers (stated → web → documented → tested → production).
- Conflict detection that **blocks** output.
- `/challenge` — adversarial pressure on claims.
- Pre-built knowledge packs (11 domains, 131 claims).
- Mill — 24-format export engine.
- Harvest — cross-sprint analytics, prediction calibration, knowledge decay.
- Orchard — multi-sprint conflict detection across parallel tracks.
- Farmer — remote permission dashboard (mobile-capable).
- Predictive scoring and calibration feedback.
- Confidence scores on compiled briefs.

---

## 7. Overlap

Both cover: decision tracking, Claude Code integration, offline-first design, git as audit trail, research/investigation support (wheat vs. SPIKE), modular skill/tool structure, discrete time-boxed work units (sprints vs. sessions), cross-reference validation, and human-in-the-loop execution.

---

## 8. Complementary Loop

**Grainulation is for: "How do we know this decision is right?"**
Strength: structured evidence accumulation with adversarial testing and confidence scoring.
Gap: doesn't guide implementation or track execution.

**Swain is for: "How do we execute this decision safely?"**
Strength: safe agent orchestration with operator oversight and drift detection.
Gap: doesn't optimize evidence gathering or provide confidence scoring.

**Together:**

1. **Grainulation (research phase):** investigate, build evidence, challenge findings, compile a brief with confidence score.
2. **Swain (execution phase):** create an Epic/Spec from the compiled brief; agents implement; ADRs constrain the work.
3. **Harvest + Retro (learning phase):** Harvest measures estimate calibration; swain retros extract learnings and feed back into the next sprint.
