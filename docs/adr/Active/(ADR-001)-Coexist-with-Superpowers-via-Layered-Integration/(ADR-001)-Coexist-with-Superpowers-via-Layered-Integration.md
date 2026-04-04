---
title: "Coexist with Superpowers via Layered Integration"
artifact: ADR-001
track: standing
status: Active
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
trove:
linked-artifacts:
  - EPIC-004
  - SPEC-008
  - SPIKE-004
depends-on-artifacts: []
---

# ADR-001: Coexist with Superpowers via Layered Integration

## Context

Swain is a decision-support and implementation-alignment system for solo developers working with AI coding agents. obra/superpowers (v5.0.1) is a complementary system providing "superpowers for your agent" — structured implementation workflows including TDD, subagent dispatch, code review, and branch management.

SPIKE-004 mapped both systems skill-by-skill and found they occupy different primary domains:
- Swain excels at the **project outer loop**: 11 artifact types, lifecycle governance, evidence pools, release automation, status tracking, session management
- Superpowers excels at the **implementation inner loop**: TDD enforcement, subagent-driven development, git worktrees, code review, systematic debugging

There is meaningful overlap in three areas: spec authoring, implementation planning, and completion verification. This overlap creates a "contested middle layer" that must be explicitly resolved.

## Decision

Adopt Option 1: **Swain owns structure, superpowers owns conversation flow.**

Three-layer model:
1. **Swain only** (project governance): Vision, Epic, Journey, Persona, ADR, Runbook, evidence pools, status, release, session, doctor
2. **Overlap** (design & planning): swain-design controls artifact format/lifecycle/cross-references; superpowers drives conversation flow (Socratic brainstorming) and implementation planning where present
3. **Superpowers only** (implementation discipline): TDD, subagent dispatch, worktrees, code review, systematic debugging, parallel agents

Key integration decisions:
- Brainstorming is selective (Visions and Personas get full Socratic flow; Stories, Spikes, ADRs do not)
- SPECs become thin contracts (acceptance criteria, ADR links, verification gate) — the heavy implementation plan section is replaced by superpowers' writing-plans output
- Task tracking flows through swain-do/bd, not TodoWrite — swain-do intercepts superpowers plans and creates bd items
- When superpowers is installed, subagent-driven development is preferred; swain-do serial execution is the fallback
- Session startup uses a lightweight preflight script instead of auto-invoking swain-doctor every session
- Completion verification broadens to all tasks (not just SPEC acceptance criteria)

## Alternatives Considered

**Option 2 — Superpowers leads the middle layer entirely:** When superpowers is installed, swain-design defers to brainstorming for spec creation and swain-do defers to writing-plans for plan creation. Rejected because superpowers' spec format (date-prefixed files in `docs/superpowers/specs/`) diverges from swain's artifact model, and swain loses control of its core artifact lifecycle.

**Option 3 — Cherry-pick techniques, don't import skills:** Swain adopts patterns from superpowers (anti-rationalization tables, Socratic questioning, subagent dispatch concepts) as enhancements to existing swain skills. No runtime dependency on superpowers. Rejected because it misses the implementation discipline benefits that require superpowers' actual enforcement (TDD deletion of pre-test code, review subagents, worktree isolation). Patterns-only adoption loses the teeth.

**Retire swain:** Superpowers covers ≤40% of swain's functional surface. Retirement would lose 11 artifact types (vs. superpowers' 2), evidence pools, release automation, project status, session management, dependency graph tooling, and ADR compliance checking. These are outside superpowers' stated scope.

## Consequences

**Positive:**
- Both systems' strengths are preserved without redundancy in their primary domains
- Superpowers' implementation discipline (TDD, subagents, review) strengthens swain's weakest area
- Swain's lifecycle governance, research infrastructure, and release automation fill superpowers' gaps
- Clear routing rules prevent skill conflicts

**Negative / Trade-offs:**
- Session startup complexity increases (preflight + conditional doctor + superpowers bootstrap + session restore)
- Plan ingestion requires an adapter between superpowers' plan format and bd's task model
- Developers must understand which system "owns" each concern — the three-layer model adds cognitive load
- Superpowers evolves independently; future versions may shift boundaries

**Open items (deferred to SPEC-008):**
- Plan ingestion parser contract between superpowers output and swain-do
- Preflight script scope and zero-token-when-clean design
- Anti-rationalization table adoption in swain-do

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Adopted | 2026-03-12 | 834c356 | Decision made during SPIKE-004 research; skipped Draft/Proposed |
