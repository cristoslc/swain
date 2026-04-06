---
title: "Commit-Hash Staleness Detection"
artifact: SPEC-273
track: implementable
status: Proposed
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
priority-weight: ""
type: ""
parent-epic: EPIC-062
parent-initiative: ""
linked-artifacts:
  - DESIGN-019
  - DESIGN-020
depends-on-artifacts:
  - SPEC-272
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Commit-Hash Staleness Detection

## Problem Statement

Evidence sidecars show that a test passed at a given commit. But if the spec, a parent design, or a linked ADR changed after that commit, the evidence is stale. No tooling detects this today. Operators must track which files changed and re-run tests by hand.

## Desired Outcomes

Staleness is derived from git metadata, not agent judgment. When any artifact in a scenario's dependency cone changes at a later commit, downstream evidence is flagged stale. Operators see what changed and when.

## External Behavior

- Each evidence sidecar stores the git commit hash at which it was created.
- "Stale" means a file in the dependency cone was changed at a commit newer than the stamp.
- The dependency cone includes: the spec, its parent design, linked ADRs, and the parent epic.
- Specgraph already walks these edges. This spec adds evidence stamp checks on top.
- Three queries:
  1. Declared scenarios with no evidence.
  2. Evidence whose stamp is older than an upstream change (stale).
  3. Evidence with no matching declared scenario (drift — overlaps SPEC-270).
- Output: a report listing each stale sidecar, the file that changed, and the commit that caused it.

## Acceptance Criteria

1. **Given** evidence stamped at commit A and the spec is unchanged since A, **when** staleness detection runs, **then** the evidence is marked fresh.

2. **Given** evidence stamped at commit A and the spec changed at commit B (B newer than A), **when** staleness detection runs, **then** the evidence is flagged stale.

3. **Given** evidence stamped at commit A and a linked ADR changed at commit B (B newer than A), **when** staleness detection runs, **then** the evidence is flagged stale.

4. **Given** evidence stamped at commit A and the parent Design changed at commit B (B newer than A), **when** staleness detection runs, **then** the evidence is flagged stale.

5. **Given** a scenario declared in the spec with no evidence sidecar, **when** staleness detection runs, **then** the scenario is flagged "no evidence."

6. **Given** one or more stale sidecars, **when** the report is built, **then** each entry names the file that changed and the commit that caused it.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Staleness is computed by tooling, never by agents.
- Uses specgraph's existing edge traversal — extends, not replaces.
- The dependency cone is: spec to parent epic, spec to linked designs, spec to linked ADRs.
- This spec does NOT re-run tests — it only detects staleness. Re-running is SPEC-274.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
