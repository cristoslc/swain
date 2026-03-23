---
title: "Centralized Artifact Number Allocation"
artifact: EPIC-043
track: container
status: Complete
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
parent-vision: VISION-001
parent-initiative: INITIATIVE-013
priority-weight: high
success-criteria:
  - A single script allocates the next artifact number for any type, replacing ad-hoc agent scanning
  - The script scans all worktrees (via `git worktree list`) and the canonical branch to find the true max, not just the local working tree
  - swain-design SKILL.md step 1 delegates to the script instead of instructing the agent to scan
  - No duplicate artifact numbers are created across concurrent worktree sessions
  - Existing scripts that allocate numbers (migrate-bugs.sh) use the centralized allocator
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Centralized Artifact Number Allocation

## Goal / Objective

Replace the ad-hoc "scan `docs/<type>/` and pick the next number" pattern in swain-design with a single, canonical script that allocates artifact numbers. The script must be worktree-safe — it scans all worktrees (`git worktree list`) and the canonical branch to find the true max across all concurrent sessions, preventing number collisions when multiple worktrees create artifacts in parallel.

## Desired Outcomes

- **Operators** stop seeing duplicate artifact numbers after merging worktree branches back to trunk.
- **Agents** get a deterministic, one-line call instead of reimplementing the scan-and-increment logic every time they create an artifact.
- **Skill authors** have a stable interface (`next-artifact-number.sh <TYPE>`) they can call from any script that needs to allocate an artifact ID.

## Scope Boundaries

**In scope:**
- New `next-artifact-number.sh` script in `skills/swain-design/scripts/`
- Worktree detection — scan all worktrees (`git worktree list`) plus `git show trunk:docs/` to find the true max across all concurrent sessions
- Update swain-design SKILL.md step 1 to call the script
- Update `migrate-bugs.sh` to use the shared allocator
- Collision detection hook (pre-commit or specwatch) that flags duplicate numbers before they merge

**Out of scope:**
- Distributed locking or a central sequence server — file-level coordination is sufficient for swain's single-operator model
- Changing the artifact numbering scheme itself (e.g., switching to UUIDs)
- Retroactive renumbering of existing artifacts

## Child Specs

_Updated as Agent Specs are created under this epic._

- **SPEC-TBD:** `next-artifact-number.sh` — core allocator script with worktree-safe branch query
- **SPEC-TBD:** swain-design SKILL.md integration — replace step 1 with script call
- **SPEC-TBD:** Collision detection — specwatch or pre-commit check for duplicate numbers
- **SPEC-TBD:** Migrate existing callers — update `migrate-bugs.sh` and any other scripts

## Key Dependencies

- Relies on `git show <branch>:<path>` or `git worktree list` for cross-worktree queries — standard git, no external deps.
- swain-design SKILL.md is the primary consumer — changes there affect every artifact creation.

## Retrospective

**Terminal state:** Complete
**Period:** 2026-03-22 — 2026-03-23 (single session)
**Related artifacts:** SPEC-156, SPEC-157, SPEC-158, SPEC-159, SPIKE-043, ADR-015

### Summary

All 5 success criteria met. Delivered a centralized allocator script (`next-artifact-number.sh`) that scans all worktrees + trunk, integrated it into SKILL.md step 1, built collision detection + renumber tools, and migrated existing callers. The detection script found 3 real number collisions already in the repo (SPEC-119, SPEC-120, SPIKE-001), retroactively validating the EPIC's premise.

Side outputs: SPIKE-043 (Phase Complexity Model) emerged from observing that not everything needs manual testing — produced a Stacey Matrix-based model for adaptive ceremony. ADR-015 (Ephemeral Tickets) emerged from the worktree cleanup experience — formalized that tickets are scaffolding, not records.

### Reflection

**What went well:**
- Critical-path ordering (SPEC-156 first, then fan out) kept all work unblocked
- TDD caught two platform-specific bugs (bash 3.2 associative arrays, `find -name` glob pattern) that manual testing would have missed
- The allocator was dogfooded immediately for SPIKE-043 creation
- Side quests (SPIKE-043, ADR-015) landed as durable artifacts rather than ephemeral observations

**What was surprising:**
- 3 real collisions existed in the repo already — the problem was more urgent than anticipated
- SPEC-158 scope grew during execution (renumber tools, swain-sync gate) and the expansion was productive, not scope creep

**Patterns observed:**
- Brainstorming adds less value when the operator arrives with a clear mental model — the chain's value was confirming design choices, not discovering intent
- Scope that expands from operator feedback during execution is healthy; the living-spec pattern works better than trying to nail down everything upfront
- Side quests that produce artifacts (spikes, ADRs) are valuable, not distractions — capture insights when they're fresh

**Bug found:** EPIC child specs section was never updated from `SPEC-TBD` placeholders to actual linked references. Filed as SPEC-162.

### Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_parallel_research.md | feedback | (existing) Launch parallel agents for multi-source research |
| feedback_retro_foreign_runtime_testing.md | feedback | (existing) TDD in isolated temp repos catches platform-specific bugs |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation; user-requested |
