---
title: "Noisy Tool-Call Pattern Audit"
artifact: SPIKE-048
track: container
status: Active
author: cristos
created: 2026-03-26
last-updated: 2026-03-26
question: "Which swain skills suffer from the multi-tool-call script discovery anti-pattern, and can they adopt the same bootstrap/dispatcher consolidation approach used in SPEC-175?"
gate: Pre-MVP
risks-addressed:
  - Operator fatigue from verbose tool call output across all skills, not just session startup
evidence-pool: ""
---

# Noisy Tool-Call Pattern Audit

## Summary

## Question

Which swain skills suffer from the multi-tool-call script discovery anti-pattern (nested `find`-based path resolution, failed-then-retry inline commands, multi-step orchestration of fixed sequences), and can they adopt the same bootstrap/dispatcher consolidation approach used in [SPEC-175](../../../spec/Complete/(SPEC-175)-Session-Bootstrap-Script-Consolidation/(SPEC-175)-Session-Bootstrap-Script-Consolidation.md)?

## Go / No-Go Criteria

- **Go (consolidation worth pursuing broadly):** 3+ skills exhibit the same anti-pattern with 2+ unnecessary visible tool calls per invocation.
- **No-Go (session-only fix is sufficient):** Fewer than 3 skills are affected, or affected skills have variable sequences that resist consolidation into a single script.

## Pivot Recommendation

If No-Go: limit the fix to [SPEC-175](../../../spec/Complete/(SPEC-175)-Session-Bootstrap-Script-Consolidation/(SPEC-175)-Session-Bootstrap-Script-Consolidation.md) (session bootstrap) and document the `find`-based discovery as a known cost of the current architecture rather than investing in a cross-skill dispatcher.

## Findings

<!-- Populated during Active phase. Survey methodology:
     1. Read every SKILL.md in .claude/skills/ and .agents/skills/
     2. For each, identify script invocations that use the find-based pattern
     3. Count the minimum Bash tool calls per invocation
     4. Classify: consolidatable (fixed sequence) vs. variable (context-dependent)
     5. Note any skills that already use single-script patterns as positive examples -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
