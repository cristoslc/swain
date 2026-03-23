---
title: "Phase Complexity Model for Adaptive Ceremony and Autonomy"
artifact: SPIKE-043
track: container
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
parent-initiative: INITIATIVE-003
question: "Can a phase complexity model — scoring problem complexity and solution complexity independently — drive adaptive decisions about ceremony depth, model selection, manual test gates, and operator consultation?"
gate: Pre-MVP
risks-addressed:
  - Over-ceremony on simple work wastes tokens and operator attention
  - Under-ceremony on complex work lets bugs and misalignment through
  - Manual test gates on trivial changes create bottlenecks without adding value
linked-artifacts:
  - INITIATIVE-017
  - INITIATIVE-019
  - SPEC-045
evidence-pool: "phase-complexity-model@6a19583"
---

# Phase Complexity Model for Adaptive Ceremony and Autonomy

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Can a phase complexity model — scoring problem complexity and solution complexity independently — drive adaptive decisions about:

1. **Ceremony depth** — which swain-design steps to run (specwatch, alignment check, index refresh) vs. fast-path
2. **Model selection** — when to use opus vs. sonnet vs. haiku for different operations
3. **Manual test gates** — when NeedsManualTest is warranted vs. when automated verification is sufficient
4. **Operator consultation** — when the agent can act autonomously vs. when it must consult the operator

Shines (the project management methodology) uses "phase complexity" to classify work by two independent axes: how complex the problem is, and how complex the solution is. A simple problem with a simple solution needs minimal process; a complex problem with a complex solution needs full ceremony. The interesting cases are the off-diagonal: a simple problem with a complex solution (implementation risk), or a complex problem with a simple solution (requires understanding but not much code).

## Prior Art to Investigate

- **Shines phase complexity model** — how does it define the axes? What thresholds does it use? How does it map to process decisions?
- **[SPEC-045](../../../spec/Complete/(SPEC-045)-Fast-Path-Authoring-Mode/(SPEC-045)-Fast-Path-Authoring-Mode.md) (Complexity tier detection)** — swain already has a rudimentary complexity tier (low/medium/high) that drives fast-path eligibility. How does that relate to phase complexity?
- **swain-model-hint comments** — the SKILL.md already uses `<!-- swain-model-hint: sonnet, effort: low -->` comments to suggest model selection per section. Could phase complexity formalize this?
- **Cynefin framework** — does the simple/complicated/complex/chaotic taxonomy map to phase complexity axes?

## Go / No-Go Criteria

**Go:** A phase complexity scoring model exists that can be evaluated at artifact creation time (from frontmatter + context) and produces actionable recommendations for at least 3 of the 4 decision domains (ceremony, model, manual test, autonomy).

**No-Go:** The model requires information not available at decision time, or produces recommendations that conflict with safety constraints (e.g., suggesting autonomous action on security-critical changes).

## Pivot Recommendation

If a single unified model doesn't work, investigate whether separate heuristics per decision domain (ceremony, model, test, autonomy) are more tractable — even if they share some input signals. The existing SPEC-045 fast-path tier could remain the ceremony heuristic while new heuristics handle model selection and autonomy.

## Findings

### 1. Prior art: Stacey Matrix (closest match to "Shines")

"Shines" was not findable as a public methodology. The closest established framework is the **Stacey Matrix** (Ralph Douglas Stacey, 1990s), which uses two independent axes:

- **Y-axis: Requirements clarity** (problem space) — ranges from clear/agreed to unclear/contested
- **X-axis: Approach certainty** (solution space) — ranges from well-known/proven to novel/unproven

The four quadrants map to process decisions:

| | Solution: Known | Solution: Novel |
|--|----------------|-----------------|
| **Problem: Clear** | **Simple** — plan-driven, minimal ceremony | **Complicated** — implementation risk, needs structured analysis |
| **Problem: Unclear** | **Complicated** — needs understanding, moderate ceremony | **Complex** — iterative, high ceremony, experiments |

This matches the operator's framing exactly: two axes, interesting off-diagonal cases, and direct mapping to process intensity.

### 2. Cynefin framework (complementary, not replacement)

Cynefin (Dave Snowden) classifies domains by the nature of cause-and-effect relationships:

| Domain | Constraint type | Action pattern | Automation fit |
|--------|----------------|---------------|----------------|
| Clear | Fixed constraints | Sense-Categorize-Respond | Fully automatable |
| Complicated | Governing constraints | Sense-Analyze-Respond | Rules-based automation, expert judgment at decision points |
| Complex | Enabling constraints | Probe-Sense-Respond | Automate scaffolding, not decisions |
| Chaotic | No constraints | Act-Sense-Respond | Alerting only |

Cynefin is a sense-making lens, not a scorable matrix. For automated process selection, Stacey is more directly useful — its axes can be scored numerically. Cynefin informs *what kind* of automation is appropriate per quadrant.

### 3. Current state in swain (SPEC-045 + model hints)

Swain has two disconnected mechanisms:

**SPEC-045 fast-path** (implemented, drives ceremony):
- Signals: artifact type (bug/fix), parent linkage, downstream deps, user language
- Decision: skip specwatch, alignment check, index refresh, two-commit stamp
- Savings: ~3,600 tokens per fast-path artifact
- Limitation: binary (fast-path or full ceremony), no gradient

**swain-model-hint** (advisory, not automated):
- Format: `<!-- swain-model-hint: sonnet, effort: low -->`
- Hard-coded per SKILL.md section, not per-artifact
- Gap: no runtime routing engine, no connection to complexity tier

**Manual test gate** (uniform, no optimization):
- All SPECs transit through NeedsManualTest regardless of complexity
- No exception path for trivial fixes

### 4. Proposed phase complexity model for swain

#### Input signals (evaluable at artifact creation time)

**Problem complexity axis (P):**
| Score | Signal | Examples |
|-------|--------|----------|
| P1 (Clear) | Bug with reproduction steps, single-behavior change, typo fix | `type: bug`, explicit repro steps, no linked designs |
| P2 (Bounded) | Feature with defined ACs, enhancement to existing behavior | `type: feature` with parent-epic, clear ACs |
| P3 (Exploratory) | Architectural change, cross-cutting concern, design decision needed | Linked DESIGN or ADR, multiple linked-artifacts, "investigate" language |

**Solution complexity axis (S):**
| Score | Signal | Examples |
|-------|--------|----------|
| S1 (Isolated) | Touches ≤3 files, no cross-skill changes, no schema migration | Single script, no depends-on-artifacts |
| S2 (Bounded) | Touches one skill or subsystem, bounded blast radius | parent-epic set, depends-on 1-2 artifacts |
| S3 (Cross-cutting) | Touches multiple skills, changes shared interfaces, migration needed | depends-on 3+ artifacts, modifies SKILL.md, changes frontmatter schema |

#### Quadrant-to-decision mapping

| Quadrant | P×S | Ceremony | Model | Manual test | Autonomy |
|----------|-----|----------|-------|-------------|----------|
| **Trivial** | P1×S1 | Fast-path | Sonnet | Skip (automated verification sufficient) | Act autonomously, report after |
| **Implementation risk** | P1×S2, P1×S3 | Full ceremony | Opus for planning, Sonnet for execution | Required (broad blast radius despite simple problem) | Consult on plan, autonomous on tasks |
| **Understanding risk** | P2×S1, P3×S1 | Standard | Opus for analysis | Skip (isolated change) | Consult on approach, autonomous on implementation |
| **Full complexity** | P2×S2+, P3×S2+ | Full ceremony + alignment check | Opus | Required | Consult at each phase gate |

#### Safety overrides (non-negotiable)

Regardless of quadrant:
- **Security-tagged artifacts** → always full ceremony + manual test + operator consultation
- **ADR compliance findings** → always surface to operator
- **First artifact of a new type** → always full ceremony (no precedent to calibrate against)
- **Artifacts touching AGENTS.md or SKILL.md** → always operator consultation (governance changes)

### 5. Relationship to existing fast-path

The proposed model is a **superset** of SPEC-045's fast-path. The current fast-path heuristic maps to the P1×S1 (Trivial) quadrant. The new model adds:
- Gradient between fast-path and full ceremony (the P1×S2 and P2×S1 cases)
- Model selection recommendations (not just ceremony skipping)
- Manual test gate optimization (skip for isolated low-problem-complexity work)
- Autonomy boundaries (act-then-report for trivial, consult for complex)

### 6. Evaluation against Go/No-Go criteria

**Go criteria: produces actionable recommendations for 3+ of 4 domains.**

| Domain | Actionable? | Notes |
|--------|------------|-------|
| Ceremony depth | Yes | Extends existing fast-path to 4 tiers |
| Model selection | Yes | Quadrant maps to opus/sonnet/haiku per operation |
| Manual test gate | Yes | Trivial and understanding-risk quadrants skip NeedsManualTest |
| Operator consultation | Yes | Trivial acts autonomously; implementation-risk consults on plan; full-complexity consults at gates |

**All 4 domains covered.** The input signals (artifact type, frontmatter fields, linked-artifacts count, depends-on count) are all available at creation time.

**Safety constraints satisfied:** Override rules prevent the model from recommending autonomous action on security-critical or governance changes.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | User-requested; investigating phase complexity as adaptive ceremony driver |
