---
title: "Artifact ID Collision Detection"
artifact: SPEC-140
track: implementable
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Artifact ID Collision Detection

## Problem Statement

swain-design assigns artifact IDs by scanning `docs/<type>/` for the next available number, but concurrent or interleaved artifact creation sessions can produce collisions — multiple artifacts of the same type sharing the same numeric ID. A single cleanup session on 2026-03-21 discovered 11 SPEC collisions and 1 EPIC collision caused by three independent batches of artifact creation that used overlapping ID ranges. Collisions silently corrupt cross-references: a `linked-artifacts: SPEC-098` entry becomes ambiguous when two different specs share that ID.

No tooling currently detects this condition. specgraph parses all artifacts but does not check for duplicate IDs within a type. swain-doctor validates many structural invariants but not ID uniqueness. swain-design's creation workflow scans for the next number but does not lock or verify against concurrent writers.

## Reproduction Steps

1. In session A, create SPEC-098 (Session Action Log)
2. In session B (before session A commits/pushes), create a different spec — swain-design scans `docs/spec/` and also assigns SPEC-098
3. Both sessions commit. Two directories now exist with `(SPEC-098)-*` names
4. No error is raised. Cross-references to SPEC-098 are now ambiguous

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Artifact creation never produces a duplicate ID within the same type. If a collision is introduced (e.g., via manual creation or merge), tooling detects and reports it.

**Actual:** Collisions are silently created and propagated. No tool reports them until a human notices ambiguous cross-references.

## Acceptance Criteria

### AC1: specgraph detects same-type ID collisions during graph build

**Given** two or more artifacts of the same type share the same numeric ID (e.g., two directories matching `(SPEC-098)-*`)
**When** `chart.sh build` runs
**Then** specgraph reports each collision as an error with both paths, and exits non-zero

### AC2: swain-doctor runs collision check and fails loudly

**Given** specgraph's collision detection is available
**When** swain-doctor runs its health checks
**Then** it invokes the collision check, reports any collisions as a FAIL finding, and does not pass the health check

### AC3: swain-design validates next available ID before assigning

**Given** swain-design is creating a new artifact
**When** it determines the next available ID number
**Then** it verifies no existing directory or file uses that ID across all phase subdirectories for the type, not just the target phase directory

## Scope & Constraints

- Detection is the primary deliverable — automated resolution (renumbering) is out of scope
- The collision check should be fast enough to run on every `chart.sh build` and every swain-doctor invocation without noticeable delay
- specgraph already walks all artifact directories during graph construction — the check should piggyback on that traversal, not add a second pass
- The swain-design creation workflow fix (AC3) is a behavioral change in the skill file, not a script change

## Implementation Approach

1. **specgraph collision detection (AC1):** During `build_graph()` in specgraph, maintain a dict of `{(type, number): [paths]}`. After traversal, emit errors for any entries with `len(paths) > 1`. Exit non-zero if collisions found.

2. **swain-doctor integration (AC2):** Add a `check_artifact_collisions()` function that invokes `chart.sh build` and parses collision errors from stderr. Report as FAIL with remediation hint: "Run swain-design audit to identify and renumber collisions."

3. **swain-design creation guard (AC3):** Update the skill file's creation workflow step 1 to scan all phase subdirectories (`Proposed/`, `Active/`, `Complete/`, `Superseded/`) when determining the next available number, not just the target directory.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | -- | Initial creation — filed after manual cleanup of 11 SPEC + 1 EPIC collision |
