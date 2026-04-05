---
title: "BDD Retrofit Migration"
artifact: SPEC-275
track: implementable
status: Proposed
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
priority-weight: ""
type: ""
parent-epic: EPIC-062
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-269
  - SPEC-270
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# BDD Retrofit Migration

## Problem Statement

Existing specs have tables with criteria and test evidence. They lack Gherkin blocks, `@id:` tags, and `@bdd:` markers. Without these, they cannot take part in BDD traceability. Dozens of specs need this change. Doing it by hand is not practical.

## Desired Outcomes

A one-time script converts existing specs to BDD format. After it runs, specs have Gherkin blocks with `@id:` tags. Tests have `@bdd:` markers. Evidence sidecars are built from current test results.

## External Behavior

- Script path: `.agents/bin/bdd-retrofit.sh`
- Input: a spec path or "all" for batch mode
- For each spec:
  1. Reads criteria from the table
  2. Creates Gherkin scenarios from each criterion
  3. Assigns `@id:` tags to each scenario
  4. Scans test files for matches by name or Evidence column
  5. Adds `@bdd:` markers to matched tests
  6. Builds evidence sidecars from current test results
- Output: changed spec, changed test files, new sidecars
- Dry-run mode: `--dry-run` shows planned changes, modifies nothing
- Report: lists specs changed, tests linked, and unmatched criteria that need manual review

## Acceptance Criteria

```gherkin
@id:AC-275.1
Scenario: Retrofit produces Gherkin scenarios from verification criteria
  Given a spec with 3 verification criteria and no Gherkin blocks
  When the retrofit script runs on that spec
  Then the spec contains 3 Gherkin scenarios each with a unique @id: tag

@id:AC-275.2
Scenario: Retrofit matches existing test by Evidence column reference
  Given a spec with a criterion whose Evidence column names a test function
  When the retrofit script runs on that spec
  Then the named test file contains a @bdd: marker linking to the criterion's @id:

@id:AC-275.3
Scenario: Unmatched criterion reported for manual review
  Given a spec with a criterion that has no matching test
  When the retrofit script runs on that spec
  Then the report lists that criterion as "needs manual review"
  And no @bdd: marker is added for that criterion

@id:AC-275.4
Scenario: Dry-run shows changes without modifying files
  Given a spec eligible for retrofit
  When the retrofit script runs with the --dry-run flag
  Then the report shows planned changes
  And no files on disk are modified

@id:AC-275.5
Scenario: Batch mode processes all specs with Verification tables
  Given multiple specs in docs/spec/ where some have Verification tables
  When the retrofit script runs with "all" as input
  Then every spec with a Verification table is processed
  And specs without Verification tables are skipped

@id:AC-275.6
Scenario: Already-migrated spec is skipped
  Given a spec that already contains Gherkin blocks
  When the retrofit script runs on that spec
  Then the spec is skipped with message "already has BDD scenarios"
  And no changes are made to that spec
```

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This is a one-time migration, not an ongoing task.
- Gherkin output is best-effort. Operators review it.
- Test matching uses Evidence column references, not semantic analysis.
- Specs that already have Gherkin blocks are skipped.
- Can run alongside SPEC-272 through SPEC-274. Only depends on notation and marker rules.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
