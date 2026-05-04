---
source-id: swain-verification-landscape
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Swain's Verification Landscape: Current State and Gaps"
author: "Swain project artifacts"
fetched: 2026-04-20
freshness-ttl: 90
url: "https://github.com/cristoslc/swain"
tags: [swain, verification, automated-testing, BDD, test-gates, verification-loop, inititatives, epics, specs]
---

# Swain's Verification Landscape: Current State and Gaps

## Overview

Swain's verification architecture is in transition. Two earlier epics — EPIC-052 (Automated Test Gates) and EPIC-062 (BDD Traceability) — defined parts of the verification story. Both are now superseded by INITIATIVE-022 (Automated Verification Loop) and its design document, DESIGN-027. This source covers the current state: what exists, what is proposed, what is missing, and the tension between shipping what is half-built versus waiting for the full architecture.

## What Exists: EPIC-052 — Automated Test Gates

EPIC-052 defined a two-phase verification gate:

**Phase 1 — Integration tests (deterministic, script-driven).** The `swain-test.sh` script (SPEC-220) detects and runs the project's test suite. It uses convention-based detection (package.json → npm test, Cargo.toml → cargo test, etc.) or a custom command declared in `.agents/testing.json`. The script exits with a structured output: pass/fail status, test command, duration, test count, and instructions for Phase 2.

**Phase 2 — Smoke tests (agent-executed, judgment-driven).** The `swain-test` skill (SPEC-221) orchestrates the agent through smoke verification. It reads spec acceptance criteria from artifact paths, exercises behavioral verification for changed skill files, runs standing project smoke tests, and falls back to generic "describe what you changed, exercise it, report what you observed" instructions when none of the above apply. The skill handles failure by retrying once. After two failures, it escalates to the operator.

**What is implemented:**
- `swain-test.sh` script (SPEC-220): Active. Detects test commands, runs them, emits structured output.
- `swain-test` skill (SPEC-221): Complete. Orchestrates the two-phase gate. 34/34 BDD tests pass.
- `bats-core` test suite: Tests for the swain-test.sh script itself, covering test command detection, artifact path resolution, and output format.

**What is NOT implemented (from EPIC-052's scope):**
- SPEC-223 (swain-sync test gate integration): Not implemented. The gate does not run automatically during sync.
- SPEC-224 (swain-release test gate integration): Not implemented. The gate does not run automatically during release.
- SPEC-225 (flat artifact migration): Not implemented. Related to organizational cleanup, not directly verification.
- SPEC-226 (evidence recording): Not implemented. No `verification-log.md` files are being appended to artifact folders. Test results do not travel with commits.

The core script and skill work in isolation but are not wired into swain-sync or swain-release. An operator must invoke swain-test manually or prompt the agent to do so. This defeats the purpose of an automated gate.

## What Is Proposed: EPIC-062 — BDD Traceability

EPIC-062 defined a system for closing the gap between spec acceptance criteria and agent test behavior:

- **Gherkin scenarios with stable IDs.** Specs can contain `@bdd`-tagged Given/When/Then blocks with unique scenario IDs.
- **`@bdd:<scenario-id>` markers in test code.** Test functions annotate themselves with the scenario they verify. This creates a bidirectional link: from spec to test and from test to spec.
- **Evidence sidecars.** Test results are stored as `test-results.json` files next to the artifacts they verify. Symlinks propagate evidence up the tree.
- **Staleness detection.** Commit hashes track whether evidence is current. If an artifact has changed since its evidence was recorded, the evidence is stale.
- **`swain-verify <scope>` command.** Runs BDD-tagged tests for a subtree without requiring an agent.

EPIC-062 has seven proposed specs (SPEC-269 through SPEC-275). None are implemented. All are in Proposed status.

## The Supersession: INITIATIVE-022 / DESIGN-027

INITIATIVE-022 (Automated Verification Loop) supersedes both EPIC-052 and EPIC-062. Its design (DESIGN-027) articulates a core insight that the earlier epics missed:

**Verification must run against the current state of the system, not the state when the spec was written.**

Specs describe a prior state. By the time implementation finishes, ADRs have been adopted, EPIC scope has shifted, and acceptance criteria may have changed. Verification that checks against the original spec is checking a world that no longer exists.

The verification loop design has five tracks:

1. **Verification design and execution.** Use prism-review's parallel agent pattern to discover existing tests that cover what changed and write new tests for gaps. Sensitivity scaling decides which agents run.
2. **Teardown report.** Aggregates verification history, agent decisions, test design, and results. Required before any trunk merge.
3. **Decision logging and retro.** Each verification cycle (pass or fail) produces a retro. Retros accumulate into a teardown narrative.
4. **Artifact alignment agent.** Iterates over active ADRs, checks EPIC scope boundaries, and validates SPEC acceptance criteria coverage. This is compliance testing (see companion source) applied to swain's own artifacts.
5. **Supersession migration.** Move EPIC-052 and EPIC-062 to Superseded status. Reparent surviving specs.

The loop's behavioral guarantees:

- No operator nagging. Failure loops back to implementation without human input (unless severity is large).
- Fresh intent snapshot. Verification reads artifact states at verification time.
- Report before merge. No trunk merge without a saved teardown report.
- Retro accumulates. Each cycle's retro builds the final narrative.
- Sensitivity scales verification. High-sensitivity changes get more scrutiny.
- Incremental loop limit. After 5 consecutive failures (configurable), escalate to operator.

## Gaps in the Current Landscape

**1. No automated gate in swain-sync or swain-release.** The swain-test skill exists but is not wired into the sync or release workflows. An operator must remember to invoke it. This is the single biggest gap. Without automated enforcement, the gate is advisory.

**2. No BDD traceability.** There is no link between spec acceptance criteria and test code. Gherkin scenarios, `@bdd` markers, evidence sidecars, and staleness detection are all proposed (EPIC-062) but none are implemented.

**3. No coverage metrics.** There is no way to answer "what percentage of spec acceptance criteria are covered by automated tests?" or "which ADR constraints have compliance checks?" The verification loop design (DESIGN-027) addresses this implicitly through the alignment agent, but no implementation exists.

**4. No CI integration.** swain-test.sh and the swain-test skill run locally. They are not integrated into any CI pipeline. The teardown report (DESIGN-027) includes post-approval hooks for CI integration, but this is designed, not implemented.

**5. No teardown report or retro integration.** DESIGN-027 defines a teardown report that aggregates verification history, agent decisions, and retros into a single narrative. This does not exist. Current work ends after the swain-test skill completes.

**6. No artifact alignment agent.** DESIGN-027 defines an agent that checks ADR compliance, EPIC scope boundaries, and SPEC AC coverage. This is the compliance testing piece (see companion source). It does not exist. Currently, ADR drift and SPEC-implementation gaps are caught only by human review.

## The Central Tension

There is a tension between two approaches:

**Ship the half-built gate.** Wire swain-test into swain-sync and swain-release (SPEC-223, SPEC-224) as originally designed. This gives the project an automated test gate immediately, even without the full verification loop architecture. The gate runs Phase 1 (integration tests) and Phase 2 (smoke tests) before every push and tag. It is imperfect (no fresh intent snapshot, no alignment agent, no retro loop) but it catches real defects.

**Hold for the full verification loop.** Wait for INITIATIVE-022 / DESIGN-027 to be designed, specified, and implemented. This gives the project a verification loop that runs against the current state, iterates automatically, produces teardown reports, and aligns artifacts. It is architecturally complete but delayed. In the meantime, the operator must manually verify every change.

DESIGN-027's supersession table shows how the surviving parts of EPIC-052 and EPIC-062 land in the new architecture. Verification-log.md, test detection, and spec AC smoke tests come from EPIC-052. Gherkin rules, `@bdd` markers, sidecars, and staleness checks come from EPIC-062. The verification loop absorbs both and adds the alignment agent, the retro loop, and the teardown report.

## What This Means for the Trove

Swain's verification landscape touches every practice in this trove:

- **Dogfooding:** swain-test Phase 2 (smoke verification) is a form of dogfooding. The agent exercises the system as a user would, using real workflows derived from spec acceptance criteria.
- **Observability-driven testing:** DESIGN-027's teardown report captures agent decisions and verification history. This is a form of observability applied to the agent's own verification process. It answers "what did the agent check and why?" not "what is the system doing right now?"
- **Compliance testing:** The artifact alignment agent (DESIGN-027, Track 4) is compliance testing applied to ADRs. It checks whether implementation code conforms to active architectural decisions. This is the ADR-as-executable-specification pattern described in the compliance testing source.
- **Testing quadrants:** swain-test Phase 1 is Q3 (technology-facing, supporting team). Phase 2 is Q2 (business-facing, critiquing product). The alignment agent is Q4 (technology-facing, critiquing product). BDD traceability (EPIC-062) is Q1 (business-facing, supporting team). Swain has coverage across all four quadrants in design, but only Q2 and Q3 in practice.

## Practical Takeaways

1. **Wire the gate before building the loop.** The half-built gate (swain-test in swain-sync and swain-release) catches real defects now. The full verification loop catches more defects later. Ship the gate first.
2. **Implement ADR compliance checks as the first alignment agent.** ADRs are the most testable artifact. They declare clear constraints. Checking "does this code follow ADR-019?" is a concrete, automatable task that delivers immediate value.
3. **Do not wait for BDD traceability to start recording evidence.** A simple `verification-log.md` that records what was tested, when, and with what result is valuable even without `@bdd` markers and sidecars.
4. **The verification loop design is sound.** The insight that verification must run against the current state (not the plan-time state) is correct and important. But the design can be implemented incrementally: gate first, alignment agent next, retro loop after that, teardown report last.