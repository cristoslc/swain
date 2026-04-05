---
title: "BDD Traceability"
artifact: EPIC-060
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: ""
success-criteria:
  - Every SPEC can hold Gherkin scenarios with stable IDs
  - Agent tests link back to declared scenarios via @bdd markers
  - Tests without @bdd markers show up as drift signals
  - Evidence sidecars tie test results to scenarios at known commits
  - Staleness detection flags evidence when artifacts change
  - swain-verify runs @bdd-tagged tests for a subtree with no agent needed
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# BDD Traceability

## Goal / Objective

Close the gap between spec criteria and agent tests. Swain uses Given/When/Then prose in specs. It gates transitions with check tables. But it lacks traceability. You should be able to trace a behavior from its spec, to the test, to proof it passed.

## Desired Outcomes

Operators can confirm agents built what the spec asked for. When a test fails or has no proof, the gap shows right away. When an agent writes a test with no matching scenario, that test stands out as drift.

Designs, Runbooks, and Journeys may carry Gherkin. Epics, Initiatives, and Visions should not. Gherkin there means the work is too broad.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- Gherkin format rules. Fenced code blocks, `@id:` tags, auto-minting.
- `@bdd:<scenario-id>` markers in test code. Drift detection.
- `test-results.json` contract for swain-do.
- Evidence sidecars with symlinks up the tree.
- Staleness detection via commit hashes.
- `swain-verify <scope>` command to run tests.
- Retrofit path for specs that use check tables.
- [DESIGN-019](../../../design/Active/(DESIGN-019)-Operator-BDD-Workflow/(DESIGN-019)-Operator-BDD-Workflow.md) and [DESIGN-020](../../../design/Active/(DESIGN-020)-Agent-BDD-Contract/(DESIGN-020)-Agent-BDD-Contract.md).

**Out of scope:**
- Runnable Gherkin pipelines. These are opt-in per project, not swain-wide.
- `.feature` file export or standalone BDD runners.
- Scenario coverage in chart.sh. This is later work.
- Artifact paths migration. Not yet.
- New artifact types. BDD fits existing ones.

## Child Specs

<!-- Updated as Agent Specs are created under this epic. -->

| Spec | Title | Status |
|------|-------|--------|
| _TBD_ | Gherkin notation convention and `@id:` auto-minting | — |
| _TBD_ | `@bdd:` test-code markers and drift detection | — |
| _TBD_ | `test-results.json` swain-do contract | — |
| _TBD_ | Evidence sidecars and symlink hierarchy | — |
| _TBD_ | Commit-hash staleness detection | — |
| _TBD_ | `swain-verify` command | — |
| _TBD_ | Retrofit migration for existing specs | — |

## Key Dependencies

- Specgraph walks dependency edges for staleness checks.
- swain-do emits test output. It will add `test-results.json`.
- spec-verify.sh gates transitions. It will add `@bdd:` checks.
- swain-doctor fixes symlinks. It will add evidence sidecar links.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | _pending_ | Initial creation from design conversation |
