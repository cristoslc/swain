---
title: "swain-status xref Integration"
artifact: SPEC-033
track: implementable
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: EPIC-013
linked-artifacts: []
depends-on-artifacts:
  - SPEC-032
addresses: []
source-issue:
swain-do: required
---

# swain-status xref Integration

## Problem Statement

Cross-reference discrepancies detected by specgraph's xref validation need to be surfaced to the operator through the swain-status dashboard. Without this integration, xref gaps are only visible by running `specgraph xref` directly — they won't appear in the regular status workflow that operators use to decide what to work on next.

## External Behavior

### swain-status.sh changes

1. **Update specgraph path:** Change the `SPECGRAPH` variable from `specgraph.sh` to `specgraph.py`.

2. **Read xref from cache:** After the specgraph cache is loaded, read the `xref` key (which is populated during `specgraph.py build`).

3. **Include xref in status cache:** Add xref data to the swain-status JSON cache so it's available for compact mode and MOTD consumption.

4. **Render xref section:** In `render_full`, add a "Cross-Reference Gaps" section after the GitHub Issues section. Show:
   - Artifacts with body mentions not declared in frontmatter (with the undeclared IDs)
   - Artifacts with missing reciprocal `linked-artifacts` edges
   - Count of stale references (frontmatter-not-in-body), if any

### Agent summary template changes

Add a new section to the agent summary template:

```
## Cross-Reference Gaps

| Artifact | Undeclared Body References | Missing Reciprocal | Action |
|----------|--------------------------|-------------------|--------|
| EPIC-005 | SPIKE-007, SPIKE-008 | — | Classify as depends-on or linked-artifacts |
| SPIKE-007 | — | EPIC-005 | Add EPIC-005 to linked-artifacts |
```

Rules:
- Only show artifacts with at least one discrepancy
- Merge body-not-in-frontmatter and missing-reciprocal into one table per artifact
- Omit the section entirely if there are no discrepancies
- The agent should suggest concrete frontmatter edits based on context

### Follow-up suggestion

When xref gaps exist, add to the follow-up suggestions:
> "There are N cross-reference gaps — want me to review and fix the frontmatter declarations?"

## Acceptance Criteria

1. **Given** specgraph cache with xref discrepancies, **when** `swain-status.sh --refresh` runs, **then** the Cross-Reference Gaps section appears in terminal output listing each artifact with its undeclared references.

2. **Given** no xref discrepancies, **when** status runs, **then** the Cross-Reference Gaps section is omitted entirely.

3. **Given** the agent summary template, **when** the agent presents status, **then** xref gaps appear in a table with artifact, undeclared references, missing reciprocals, and suggested action.

4. **Given** xref data in the status cache, **when** `--compact` mode runs, **then** a one-line "xref: N gaps" line is included if gaps exist.

5. **Given** the specgraph path reference in swain-status.sh, **when** updated to specgraph.py, **then** status collection works identically (same cache format minus the new xref key).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. Cache with xref discrepancies → Cross-Reference Gaps section appears | swa-fy5d integration test: 67 xref gaps rendered in terminal output | ✅ |
| 2. No discrepancies → section omitted | Conditional rendering based on xref_count > 0 | ✅ |
| 3. Agent summary template has xref table | references/agent-summary-template.md updated with Cross-Reference Gaps section | ✅ |
| 4. --compact shows xref: N gaps | swa-fy5d verified: "xref: 67 gaps" in compact output | ✅ |
| 5. specgraph path updated to .py | SPECGRAPH variable at line 21 points to specgraph.py | ✅ |

## Scope & Constraints

- swain-status.sh remains in bash — it reads the specgraph JSON cache, not the Python code
- The cache format is backward-compatible: existing keys unchanged, `xref` is additive
- If `xref` key is absent from cache (e.g., during migration), the section is silently omitted

## Implementation Approach

1. **Update specgraph path** in swain-status.sh from `.sh` to `.py`.

2. **Add xref reading** to `collect_artifacts` — extract xref counts and data from the specgraph cache.

3. **Add render section** to `render_full` — jq query over the xref data to format the terminal output.

4. **Update compact mode** — add xref gap count if > 0.

5. **Update agent summary template** — add the Cross-Reference Gaps section with table format and rules.

6. **Manual test** — run `/swain-status` and verify the new section appears when there are known xref gaps (e.g., the EPIC-005/SPIKE-007 case).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Active | 2026-03-14 | acf66cf | Implementation started — specgraph path update and xref template |
| Complete | 2026-03-14 | c51ed6d | xref integration verified — 67 gaps surfaced, compact mode shows count, bug in missing_reciprocal rendering fixed |
