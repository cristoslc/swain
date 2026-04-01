---
title: "Doctor Artifact Index Staleness Repair"
artifact: SPEC-227
track: implementable
status: Complete
author: operator
created: 2026-04-01
last-updated: 2026-04-01
priority-weight: medium
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-013
linked-artifacts:
  - INITIATIVE-013
  - SPEC-047
  - SPEC-222
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Doctor Artifact Index Staleness Repair

## Problem Statement

`list-*.md` files under `docs/` are for people, not tooling. `rebuild-index.sh` refreshes them later, not on every edit. So they can drift from the real frontmatter. Today `swain-doctor` never checks them. A session can start with stale or missing index files and the operator gets no signal.

## Desired Outcomes

Session-start health checks keep index files in sync. If an index is stale or missing, doctor repairs it and reports the repair. If the files are current, doctor stays quiet.

## External Behavior

When `swain-doctor` runs, it checks the index files under `docs/` that come from frontmatter. That includes `list-spec.md`, `list-epic.md`, `list-spike.md`, `list-adr.md`, `list-persona.md`, `list-runbook.md`, `list-design.md`, `list-vision.md`, `list-journey.md`, and `list-initiative.md` when the rebuild script supports it.

- If an index is missing, doctor regenerates it with `rebuild-index.sh` and reports an `advisory`.
- If an index exists but differs from freshly generated output, doctor replaces it and reports an `advisory`.
- If all supported indices already match the rebuilt output, doctor reports `ok`.
- Unsupported artifact types are skipped without failing the check.

## Acceptance Criteria

- Given a stale `docs/spec/list-spec.md`, when `swain-doctor` runs, then it regenerates the file and reports an `advisory`.
- Given a missing supported index file, when `swain-doctor` runs, then it recreates the file and reports an `advisory`.
- Given supported artifact indices are already current, when `swain-doctor` runs, then the docs-index check reports `ok` and makes no file changes.
- Given the repair has already run, when `swain-doctor` runs again, then the docs-index check reports `ok` and makes no new changes.

## Reproduction Steps

1. Start from a repo where `docs/spec/list-spec.md` is older than the artifact frontmatter it summarizes.
2. Run:
   ```bash
   bash skills/swain-design/scripts/rebuild-index.sh spec
   git diff -- docs/spec/list-spec.md
   ```
3. Observe that the generated index differs from the checked-in file.
4. Run:
   ```bash
   bash skills/swain-doctor/scripts/swain-doctor.sh | jq '.checks[] | select(.name|test("index|docs"))'
   ```
5. Observe that no docs-index check is reported, so doctor does not surface or repair the stale index.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Doctor detects stale or missing index files, rebuilds them, and reports the repair.

**Actual:** Doctor never inspects these files, so stale or missing indices can sit until some other workflow runs `rebuild-index.sh`.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Stale spec index repaired with advisory | `bash skills/swain-doctor/tests/test-swain-doctor-sh.sh` Test 16 | Pass |
| Missing spec index recreated with advisory | `bash skills/swain-doctor/tests/test-swain-doctor-sh.sh` Test 17 | Pass |
| Clean repo reports `artifact_indexes: ok` | `bash skills/swain-doctor/scripts/swain-doctor.sh | jq '.checks[] | select(.name == "artifact_indexes")'` | Pass |
| Live stale index smoke repaired | Manual smoke: appended sentinel to `docs/spec/list-spec.md`, ran doctor, confirmed advisory + sentinel removed | Pass |

## Scope & Constraints

- Use the existing `skills/swain-design/scripts/rebuild-index.sh` repair path.
- Keep the check deterministic.
- Do not turn stale indices into a blocking failure.
- Check only artifact types that the rebuild script supports in the current repo state.

## Implementation Approach

1. Add a doctor check that enumerates supported artifact index types, runs `rebuild-index.sh` for each, and detects whether the generated file changed.
2. Report `advisory` with repaired index names when doctor updates one or more files. Otherwise report `ok`.
3. Add a regression test that makes `docs/spec/list-spec.md` stale, runs doctor, verifies the repair, then reruns doctor to verify a clean second pass.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | — | Initial creation |
| Complete | 2026-04-01 | — | Implemented doctor artifact index repair, verified with tests and live smoke |
