---
title: "Gherkin Notation Convention"
artifact: SPEC-269
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
  - ADR-032
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Gherkin Notation Convention

## Problem Statement

Swain specs use prose Given/When/Then in acceptance criteria, but the format is loose. No scenario has a stable ID. Agents and tools cannot trace a scenario from its source to a test. This spec sets the Gherkin rules for swain artifacts.

## Desired Outcomes

Every behavioral scenario in a spec or standing-track artifact has a machine-readable format and a stable ID. Agents can parse scenarios without guessing. Tools can index, validate, and cross-reference them.

## External Behavior

Gherkin blocks live in fenced code blocks (` ```gherkin `) inside any artifact's markdown.

Each scenario gets a `@id:<short-uuid>` tag. The tag is an 8-character hex string. It sits on the line before `Scenario:`, using native Gherkin tag syntax.

`@id:` tags are stable. Once minted, a tag persists for the scenario's lifetime. Edits to the scenario text do not change its tag.

**Track rules:**

- **Implementable-track** (SPEC): Gherkin is required when acceptance criteria describe behavior.
- **Standing-track** (Design, Runbook, Journey): Gherkin is allowed but not required.
- **Container-track** (Epic, Initiative, Vision): Gherkin is discouraged. Its presence signals work that has not been broken down.

**Auto-minting:** When a Gherkin block lacks an `@id:` tag, `swain-doctor` or a pre-commit hook mints one.

**Duplicate detection:** `swain-doctor` scans all artifacts for duplicate `@id:` tags. When it finds a clash, it re-mints the tag on the newer one.

## Acceptance Criteria

```gherkin
Feature: Gherkin notation convention

  Scenario: Valid Gherkin in a SPEC artifact
    Given an agent writes a SPEC with acceptance criteria
    When the criteria are placed in a fenced gherkin code block
    And each scenario has an @id tag with an 8-char hex value
    Then the artifact passes swain-doctor validation

  Scenario: Auto-mint missing @id tag
    Given a SPEC contains a gherkin block with a Scenario line
    And the scenario has no @id tag
    When swain-doctor runs
    Then it mints a new 8-char hex @id tag on the line before Scenario
    And the rest of the scenario text stays the same

  Scenario: Duplicate @id across two artifacts
    Given artifact A has a scenario with @id:abcd1234
    And artifact B has a different scenario with @id:abcd1234
    When swain-doctor runs
    Then it flags the duplicate
    And it re-mints the @id on the artifact with the later created date

  Scenario: Gherkin in a container-track artifact
    Given an Epic artifact contains a fenced gherkin block
    When swain-doctor runs
    Then it emits a warning "Gherkin in container-track artifact signals undecomposed work"
    And validation still passes

  Scenario: Existing @id preserved on scenario edit
    Given a scenario has @id:beef0001
    And an agent edits the Given/When/Then text of that scenario
    When the artifact is saved
    Then the @id tag remains beef0001

  Scenario: Standing-track artifact with optional Gherkin
    Given a Design artifact contains a fenced gherkin block
    And each scenario has an @id tag
    When swain-doctor runs
    Then the artifact passes validation without warnings
```

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- No `.feature` file export (ADR-032).
- No Gherkin linting beyond basic structure checks (has `Scenario:`, has `Given`/`When`/`Then`).
- Auto-minting uses short UUIDs (8-char hex), not sequential numbers.
- This spec does NOT cover test-code markers (`@bdd:`) -- that is SPEC-270.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
