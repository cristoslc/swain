---
title: "Centralized Artifact Number Allocation"
artifact: EPIC-043
track: container
status: Active
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

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation; user-requested |
