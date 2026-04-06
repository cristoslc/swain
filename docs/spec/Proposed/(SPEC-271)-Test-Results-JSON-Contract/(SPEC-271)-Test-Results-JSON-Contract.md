---
title: "Test Results JSON Contract"
artifact: SPEC-271
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
  - DESIGN-020
depends-on-artifacts:
  - SPEC-270
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Test Results JSON Contract

## Problem Statement

Agents run tests but produce no structured output that tooling can consume. Without a standard format, evidence sidecars cannot be built and swain-verify cannot work without an agent in the loop.

## Desired Outcomes

After every test run, agents produce a `test-results.json` file in a known location with a known schema. Tooling can read this file to build evidence sidecars, check coverage, and detect drift — all without calling an agent.

## External Behavior

- File: `docs/spec/<Phase>/(SPEC-NNN)-Title/evidence/test-results.json`
- Schema (v1):

```json
[
  {
    "bdd_id": "sc-a1b2c3",
    "test": "test_name",
    "status": "pass",
    "commit": "abc1234",
    "timestamp": "2026-04-05T12:00:00Z"
  }
]
```

- `bdd_id`: the `@id:` from the scenario, or `null` for tests without `@bdd:` markers.
- `status`: one of `pass`, `fail`, `error`, `skip`.
- `commit`: current git commit hash when tests ran.
- `timestamp`: ISO 8601 UTC.
- Top-level `schema_version: 1` field (or in a wrapper object — decide in AC).
- Tests without `@bdd:` markers get `"bdd_id": null` to make drift visible in data.
- swain-do is extended to produce this file after test runs.

## Acceptance Criteria

```gherkin
@id:sc-271-a1 @bdd:SPEC-271/AC-1
Scenario: Agent produces test-results.json after a test run
  Given an agent runs the test suite for a spec
  When all tests finish
  Then a test-results.json file exists in the spec's evidence/ folder

@id:sc-271-b2 @bdd:SPEC-271/AC-2
Scenario: BDD-marked tests have matching entries
  Given a test file contains @bdd: markers with known IDs
  When the agent writes test-results.json
  Then every marked test has an entry whose bdd_id matches its @id tag

@id:sc-271-c3 @bdd:SPEC-271/AC-3
Scenario: Unmarked tests appear with null bdd_id
  Given a test file contains tests without @bdd: markers
  When the agent writes test-results.json
  Then those tests appear with bdd_id set to null

@id:sc-271-d4 @bdd:SPEC-271/AC-4
Scenario: Missing test-results.json triggers no-evidence warning
  Given a spec has no test-results.json in its evidence folder
  When swain-verify checks the spec
  Then it flags "no evidence" for that spec

@id:sc-271-e5 @bdd:SPEC-271/AC-5
Scenario: Malformed JSON triggers parse error
  Given test-results.json exists but contains invalid JSON
  When swain-verify reads the file
  Then it reports a parse error and skips the spec

@id:sc-271-f6 @bdd:SPEC-271/AC-6
Scenario: Schema version field is present
  Given an agent writes test-results.json
  When tooling reads the file
  Then the file includes a schema_version field set to 1
```

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This spec defines the schema and file location only.
- Producing evidence sidecars from this file is SPEC-272.
- Staleness checking is SPEC-273.
- The schema is versioned. Breaking changes need a swain-doctor migration.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
