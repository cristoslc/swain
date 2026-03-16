---
title: "SPEC-037: Specgraph ready Leaks Standing-Track Artifacts"
artifact: SPEC-037
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: bug
parent-epic: ""
linked-artifacts:
  - ADR-003
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Specgraph `ready` Leaks Standing-Track Artifacts

## Problem Statement

`specgraph.sh ready` returns decision/standing-track artifacts (ADR, PERSONA, JOURNEY, VISION, RUNBOOK, DESIGN) in "Active" status as if they were actionable implementation work. Active is the terminal/resolved state for these types — they should not appear in the ready list.

The `do_next` and `do_overview` functions correctly use a type-aware `is_resolved` helper that treats Active standing-track artifacts as resolved. But `do_ready` uses an inline status regex that only checks explicit terminal statuses (Complete, Retired, Superseded, etc.), missing the standing-track pattern entirely.

## External Behavior

**Before fix:** `specgraph.sh ready` returns Active ADRs, PERSONAs, JOURNEYs, VISIONs, RUNBOOKs, and DESIGNs alongside genuinely actionable SPECs and EPICs.

**After fix:** `specgraph.sh ready` only returns artifacts that are genuinely unresolved and actionable. Standing-track artifacts at Active status are excluded, consistent with `next` and `overview`.

## Acceptance Criteria

- Given an ADR in Active status, when running `specgraph.sh ready`, then the ADR does not appear in the output
- Given a PERSONA in Active status, when running `specgraph.sh ready`, then the PERSONA does not appear
- Given a VISION in Active status, when running `specgraph.sh ready`, then the VISION does not appear
- Given a SPEC in Proposed status with a depends-on an Active ADR, when running `specgraph.sh ready`, then the SPEC appears (because the ADR dependency is resolved)
- Given `specgraph.sh ready` output, it is consistent with the Ready section of `specgraph.sh overview`

## Reproduction Steps

1. Have Active ADRs, PERSONAs, JOURNEYs, or VISIONs in the docs directory
2. Run `specgraph.sh ready`
3. Observe that these standing-track artifacts appear in the output as if they are actionable work

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** `ready` returns only genuinely unresolved, actionable artifacts — the same set shown in the Ready section of `overview`.

**Actual:** `ready` also returns Active standing-track artifacts (ADR, PERSONA, JOURNEY, VISION, RUNBOOK, DESIGN), inflating the actionable work list with resolved decision artifacts.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| specgraph ready excludes Active standing-track artifacts | `specgraph.sh ready` + `specgraph.py ready` — no ADR/PERSONA/VISION/JOURNEY/RUNBOOK/DESIGN in output | PASS |
| Uses same is_resolved pattern as do_next/do_overview | Code inspection: bash uses is_resolved def; Python uses resolved.py _STANDING_TYPES | PASS |

## Scope & Constraints

- Fix is limited to `do_ready()` in `specgraph.sh`
- Must use the same `is_resolved` pattern already used by `do_next()` and `do_overview()`
- No changes to other commands or the graph structure

## Implementation Approach

1. Extract the `is_resolved` jq function (already defined in `do_next` and `do_overview`) into the `do_ready` jq filter
2. Replace the inline status regex in `do_ready` with the type-aware `is_resolved` check — both for filtering the node list and for checking dependency resolution
3. Verify output matches the Ready section of `overview`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | | Initial creation — bug report |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Complete | 2026-03-14 | dacbf2c | Standing-track exclusion already in HEAD — verified correct in both bash and Python specgraph |
