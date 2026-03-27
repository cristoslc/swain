---
title: "Superpowers chain skips artifact creation"
artifact: SPEC-154
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: "agent-alignment-monitoring@8047381"
source-issue: ""
swain-do: required
---

# Superpowers chain skips artifact creation

## Problem Statement

The superpowers skill chaining table (AGENTS.md, swain-design SKILL.md, brainstorming SKILL.md) defines the chain for SPEC implementation as:

> brainstorming → writing-plans → swain-do

This skips swain-design artifact creation entirely. Brainstorming's terminal state is declared as "invoking writing-plans" — but writing-plans operates on a single spec, and there are no swain-design artifacts (epic, specs) to write plans *for* until swain-design creates them.

The correct chain should be:

> brainstorming → **swain-design** (create artifacts) → per-spec **writing-plans** → **swain-do** (alignment checks + execution)

## Desired Outcomes

The superpowers chain correctly routes through swain-design for artifact creation before any implementation planning begins. Each spec gets its own writing-plans cycle. swain-do receives both the writing-plans output AND the swain-design artifacts, enabling alignment checks during execution.

## Reproduction Steps

1. User says "new SPEC, build X"
2. Superpowers chain triggers: brainstorming runs
3. Brainstorming completes design, writes design doc, and immediately invokes writing-plans
4. writing-plans creates an implementation plan — but for what? No SPEC artifact exists yet
5. swain-do receives a plan with no corresponding swain-design artifact to align against

## Severity

high — This is a governance chain bug that causes every brainstorming session to skip artifact creation. The vk4-swain compliance audit (trove: agent-alignment-monitoring) documented this exact failure mode: agents bypass swain-design because the chain doesn't route through it.

## Expected vs. Actual Behavior

**Expected:**
1. brainstorming explores the idea and produces a design doc
2. swain-design creates formal artifacts (epic + specs) from the design
3. For each spec coming up for implementation: writing-plans creates an implementation plan
4. swain-do ingests the plan, creates tk tickets, and oversees execution with alignment checks against the swain-design artifacts and superpowers verification gates

**Actual:**
1. brainstorming produces a design doc
2. brainstorming invokes writing-plans directly (skipping swain-design)
3. writing-plans creates a plan with no formal spec artifact
4. swain-do has no artifact to align against

## Acceptance Criteria

- Given brainstorming completes, when it transitions to its terminal state, then it invokes swain-design (not writing-plans) as the next skill
- Given swain-design creates spec artifacts from a brainstorming design, when a spec comes up for implementation, then writing-plans is invoked per-spec (not once for the whole design)
- Given swain-do receives a writing-plans output, then it can cross-reference the plan against the corresponding SPEC artifact for alignment checks
- Given AGENTS.md § Superpowers skill chaining, then chain point #2 reads: "SPEC comes up for implementation → brainstorming → swain-design → per-spec writing-plans → swain-do"
- Given brainstorming SKILL.md, then the terminal state declaration says swain-design (not writing-plans)
- Given swain-design SKILL.md § Superpowers integration, then the chain description matches the corrected flow

## Affected Files

1. `AGENTS.md` (or `AGENTS.content.md` per governance pathway) — § Superpowers skill chaining table, chain point #2
2. `.claude/skills/brainstorming/SKILL.md` — terminal state declaration ("The terminal state is invoking writing-plans" → "The terminal state is invoking swain-design")
3. `.claude/skills/swain-design/SKILL.md` — § Superpowers integration, chain description

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This is a skill file and governance doc fix — no scripts or code changes
- The brainstorming skill is a superpowers skill (`.claude/skills/` or `.agents/skills/`), not a swain skill — changes there affect all projects using superpowers
- AGENTS.md changes must go through `AGENTS.content.md` per the governance pathway feedback memory

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
