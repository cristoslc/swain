---
title: "swain-design SKILL.md Allocator Integration"
artifact: SPEC-157
track: implementable
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: enhancement
parent-epic: EPIC-043
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-156
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-design SKILL.md Allocator Integration

## Problem Statement

swain-design SKILL.md step 1 currently instructs the agent to "Scan `docs/<type>/` (recursively, across all phase subdirectories) to determine the next available number." This is vague, error-prone, and not worktree-safe. Once [SPEC-156](../(SPEC-156)-Next-Artifact-Number-Script/(SPEC-156)-Next-Artifact-Number-Script.md) delivers the allocator script, step 1 should delegate to it.

## Desired Outcomes

- Agents no longer reimplement scanning logic — they call a script and get a number.
- The SKILL.md instruction is unambiguous: one bash command, one number back.

## External Behavior

**Change:** Replace SKILL.md step 1 text with:

```
1. Allocate the next artifact number:
   ```bash
   bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/next-artifact-number.sh' -print -quit 2>/dev/null)" <TYPE>
   ```
   Use the returned number for the artifact ID.
```

**No other steps change** — step 2 onward remains as-is.

## Acceptance Criteria

- **Given** the updated SKILL.md, **when** an agent reads step 1, **then** the instruction is a single script invocation (not a scan-and-count procedure).
- **Given** SPEC-156's script is not yet available (e.g., older branch), **when** the agent reads step 1, **then** the `find` pattern fails gracefully and the agent can fall back to manual scanning. (Document the fallback in the step.)
- **Given** the updated SKILL.md, **when** creating any artifact type, **then** the number allocation follows the same code path regardless of type.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only modifies `skills/swain-design/SKILL.md` (the step 1 text).
- Must include a fallback note for environments where the script isn't available.
- Does not change any other skill files that might reference step 1.

## Implementation Approach

1. Edit SKILL.md step 1 to replace the scanning instruction with the script call.
2. Add a brief fallback note: "If the script is not found, scan `docs/<type>/` recursively for the highest existing number and increment."
3. Verify the `find` pattern resolves correctly from the repo root.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested decomposition of EPIC-043 |
