---
title: "Investigate specwatch Scan Timeout"
artifact: SPEC-316
track: implementable
status: Proposed
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Investigate specwatch Scan Timeout

## Problem Statement

`specwatch.sh scan` exceeded the 120-second timeout during post-creation artifact validation. This blocks the swain-design creation workflow and makes it unreliable — agents can't complete the artifact creation ceremony without skipping the scan step.

## Desired Outcomes

specwatch scans complete within a reasonable time (under 30 seconds for a project of this size). The scan is a quality gate, not a bottleneck.

## External Behavior

**Preconditions:** A project with ~80+ artifacts across multiple types (SPEC, EPIC, ADR, etc.).

**Expected:** `specwatch.sh scan` completes in under 30 seconds and reports findings.

**Actual:** The scan hangs or runs indefinitely, exceeding 120 seconds before being killed.

## Acceptance Criteria

1. specwatch scan completes in under 30 seconds on the current repo.
2. The root cause of the timeout is identified and documented (e.g., filesystem walk pattern, subprocess spawning, regex complexity).
3. A fix or optimization is applied and verified with a timed run.

## Reproduction Steps

1. Run `bash "$(git rev-parse --show-toplevel)/.agents/bin/specwatch.sh" scan`
2. Observe that the command does not return within 120 seconds.

## Severity

high — blocks artifact creation ceremony, forces agents to skip a quality gate.

## Expected vs. Actual Behavior

**Expected:** Scan completes, prints findings (or "OK"), exits within seconds.

**Actual:** Scan never returns within 120 seconds. Process must be killed.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Investigate and fix the scan performance issue.
- Do not remove the scan from the workflow — it's a quality gate.
- Profile `specwatch.sh` to identify the bottleneck (e.g., `time bash -x specwatch.sh scan`).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-14 | e3fbc288 | Initial creation |