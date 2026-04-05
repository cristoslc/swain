---
title: "Swain-Verify Command"
artifact: SPEC-274
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
depends-on-artifacts:
  - SPEC-271
  - SPEC-272
  - SPEC-273
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Swain-Verify Command

## Problem Statement

Running BDD-tagged tests today requires an agent in the loop. No command collects `@bdd:`-tagged tests for a scope, runs them, and produces results. Operators must start an agent session just to run regression tests.

## Desired Outcomes

A single command — `swain-verify <scope>` — collects tests, runs them, and reports pass/fail per scenario. It produces test-results.json and evidence sidecars. It works without an agent.

## External Behavior

- Command: `swain-verify <scope>` where scope is a SPEC ID, DESIGN ID, or EPIC ID.
- For a SPEC: finds test files with `@bdd:` markers for that spec's scenarios, runs them, and writes test-results.json and evidence sidecars.
- For a DESIGN or EPIC: recurses into child specs and runs all their BDD-tagged tests.
- Output: per-scenario pass/fail with links to evidence sidecars.
- Reports stale evidence (SPEC-273), undeclared behaviors (tests without `@bdd:`), and untested scenarios.
- Exit code: 0 means all scenarios pass and no drift. 1 means failures or drift found.
- Produces or updates test-results.json per the SPEC-271 schema.
- Generates or overwrites evidence sidecars per SPEC-272.

## Acceptance Criteria

### Scenario 1: Verify a single spec

**Given** SPEC-269 has three BDD scenarios and two test files carry `@bdd:` markers for them
**When** the operator runs `swain-verify SPEC-269`
**Then** the command runs all tagged tests and reports pass/fail for each scenario.

### Scenario 2: Verify an epic subtree

**Given** EPIC-062 has child specs SPEC-269 through SPEC-275, each with BDD-tagged tests
**When** the operator runs `swain-verify EPIC-062`
**Then** the command runs all child specs' BDD tests and reports results grouped by spec.

### Scenario 3: Clean run exits zero

**Given** all BDD scenarios for a scope pass and no staleness drift exists
**When** the operator runs `swain-verify <scope>`
**Then** the exit code is 0.

### Scenario 4: Failure exits non-zero

**Given** one scenario's test fails
**When** the operator runs `swain-verify <scope>`
**Then** the exit code is 1 and the report names the failing scenario and its test file.

### Scenario 5: Undeclared behavior flagged

**Given** a test file tests spec behavior but has no `@bdd:` marker
**When** the operator runs `swain-verify <scope>`
**Then** the drift section of the report lists that test as undeclared behavior.

### Scenario 6: No tests found

**Given** a spec has scenarios but no test files carry matching `@bdd:` markers
**When** the operator runs `swain-verify <scope>`
**Then** the report prints "no BDD tests found for <scope>" and exits with code 1.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This is a shell script, not an agent skill. It must work without Claude or any agent.
- Test runner detection: reads the framework from project config or uses a default (pytest, jest, bats).
- Does NOT modify specs or artifacts — read-only except for the evidence/ directory.
- Staleness detection delegates to the logic defined in SPEC-273.
- The script lives in `.agents/bin/swain-verify.sh`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
