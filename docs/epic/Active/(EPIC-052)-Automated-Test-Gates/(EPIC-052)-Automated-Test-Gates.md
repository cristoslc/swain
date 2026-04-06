---
title: "Automated Test Gates"
artifact: EPIC-052
track: container
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
parent-vision: VISION-005
parent-initiative: INITIATIVE-004
priority-weight: high
success-criteria:
  - swain-sync enforces integration and smoke test verification before every push
  - swain-release enforces integration and smoke test verification before every tag
  - Test commands are auto-detected by convention or declared via .agents/testing.json
  - Smoke instructions are assembled from active spec ACs, standing project tests, and skill detection
  - Verification evidence is recorded in artifact verification-log.md files and commit messages
  - All artifact types use folder structure — no flat files permitted
  - SPEC-215 consumer integration test harness is parented under this epic
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Automated Test Gates

## Goal / Objective

Eliminate the need for the operator to manually ask "did you run integration tests?" and "did you run smoke tests?" before every worktree-to-trunk merge and release. This gate has caught real defects on every project, every session — it must be automatic.

The `swain-test` skill and `.agents/bin/swain-test.sh` script enforce two-phase verification as a hard gate in swain-sync and swain-release. Phase 1 runs deterministic integration tests. Phase 2 directs the agent through smoke verification using evidence assembled from spec acceptance criteria, project standing tests, and skill behavioral checks.

## Desired Outcomes

The operator no longer needs to intervene before merges. Agents self-verify before pushing. Problems are caught by the gate rather than discovered on trunk. The verification record travels with the code in git history and in artifact folders — giving the operator visibility into what was tested without needing to ask.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- `swain-test.sh` script: convention-based test detection, `.agents/testing.json` support, integration test execution, smoke instruction assembly (spec ACs, skill detection, standing tests, fallback)
- `swain-test` skill: orchestrates both phases, retry logic, operator escalation after 2 failures, evidence collection
- Evidence recording: append-only `verification-log.md` in artifact folders, commit message annotation
- swain-sync integration: gate runs after commit (Step 5), before push (Step 6); re-runs on each worktree retry
- swain-release integration: gate runs after README gate (Step 5.7), before tag creation (Step 6)
- Flat artifact migration: SPEC-183 folderization, template enforcement going forward

**Out of scope:**
- Editing `finishing-a-development-branch` (superpowers, not ours)
- swain-doctor or swain-init nudges to create `.agents/testing.json`
- Test result caching across sessions
- Coverage metrics or reporting beyond pass/fail
- Concurrent worktree verification-log conflict resolution (defer until observed)
- swain-do integration (test evidence does not feed back into task status — may revisit)

## Child Specs

- [SPEC-215](../../../spec/Active/(SPEC-215)-Consumer-Integration-Test-Harness/(SPEC-215)-Consumer-Integration-Test-Harness.md) — Consumer integration test harness (re-parented)
- [SPEC-220](../../../spec/Active/(SPEC-220)-swain-test-sh-Script/(SPEC-220)-swain-test-sh-Script.md) — swain-test.sh script
- [SPEC-221](../../../spec/Active/(SPEC-221)-swain-test-Skill/(SPEC-221)-swain-test-Skill.md) — swain-test skill
- [SPEC-226](../../../spec/Active/(SPEC-226)-Verification-Evidence-Recording/(SPEC-226)-Verification-Evidence-Recording.md) — Evidence recording
- [SPEC-223](../../../spec/Active/(SPEC-223)-swain-sync-Test-Gate-Integration/(SPEC-223)-swain-sync-Test-Gate-Integration.md) — swain-sync integration
- [SPEC-224](../../../spec/Active/(SPEC-224)-swain-release-Test-Gate-Integration/(SPEC-224)-swain-release-Test-Gate-Integration.md) — swain-release integration
- [SPEC-225](../../../spec/Active/(SPEC-225)-Flat-Artifact-Migration/(SPEC-225)-Flat-Artifact-Migration.md) — Flat artifact migration

## Key Dependencies

- [SPEC-024](../../../spec/Complete/(SPEC-024)-Pre-Commit-Verification-In-Sync/(SPEC-024)-Pre-Commit-Verification-In-Sync.md) (Complete) — pre-commit hook verification in swain-sync (existing gate this extends)
- [SPEC-211](../../../spec/Complete/(SPEC-211)-Release-README-Gate/(SPEC-211)-Release-README-Gate.md) (Complete) — README gate in swain-release (gate this follows in the insertion order)
- [ADR-011](../../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) — worktree landing via merge with retry (the retry loop where the gate must re-run)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation from approved brainstorming design |
