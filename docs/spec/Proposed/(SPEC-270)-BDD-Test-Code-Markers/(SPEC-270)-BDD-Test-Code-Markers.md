---
title: "BDD Test-Code Markers"
artifact: SPEC-270
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
  - SPEC-269
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# BDD Test-Code Markers

## Problem Statement

Agents write tests from spec scenarios. But nothing links a test back to the scenario it covers. Without that link, you cannot tell which tests match which behaviors. Unlinked tests are blind spots. They may test things no spec declared.

## Desired Outcomes

Each agent test traces to a named scenario. Tests with no link stand out as drift. The rule works in Python, JS, and Bash.

## External Behavior

- Place a comment marker before the test function or block.
- The marker format is the comment char plus a tag: `# @bdd:sc-xxx` or `// @bdd:sc-xxx`.
- One marker per test. One test links to one scenario. Many tests can share a scenario.
- Add the marker at RED phase, before any code that makes the test pass.
- A test with no marker is a drift signal.
- A marker that points to a missing ID is an orphan.

## Acceptance Criteria

### Scenario: Valid marker links test to scenario
<!-- @id:sc-270-valid-marker -->

> **Given** a test has a marker that names a known scenario  
> **When** a scan runs  
> **Then** the test traces to that scenario  

### Scenario: Missing marker flags drift
<!-- @id:sc-270-missing-marker -->

> **Given** a test has no marker  
> **When** a drift scan runs  
> **Then** the scan flags the test as undeclared  

### Scenario: Bad ID flags orphan
<!-- @id:sc-270-orphan-marker -->

> **Given** a test has a marker with an ID  
> **And** no scenario carries that ID  
> **When** an orphan scan runs  
> **Then** the scan flags the marker as orphaned  

### Scenario: Many tests share one scenario
<!-- @id:sc-270-multi-test-same-scenario -->

> **Given** two tests both name the same scenario  
> **When** a scan runs  
> **Then** both tests are valid  

### Scenario: Marker added at RED phase
<!-- @id:sc-270-red-phase -->

> **Given** an agent writes a new test at RED phase  
> **When** the test is saved  
> **Then** the marker is present before any passing code  

### Scenario: Marker works across languages
<!-- @id:sc-270-cross-language -->

> **Given** test files in Python, Bash, and JS  
> **When** each file uses its own comment style with the tag  
> **Then** a scan finds all markers  

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Markers are comments, not code that runs.
- This spec does not produce test-results.json. That is SPEC-271.
- Drift detection is a scan and report, not a gate that blocks.
- Orphan detection checks markers against known IDs in the artifact graph.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
