---
title: "swain-test.sh script"
artifact: SPEC-220
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: feature
parent-epic: EPIC-052
parent-initiative: ""
linked-artifacts:
  - EPIC-052
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-test.sh script

## Problem Statement

swain-sync and swain-release have no automated test gate. Integration tests are never run before push or tag. The operator must manually prompt every agent session. This misses defects that get caught only when the operator remembers to ask.

## Desired Outcomes

A shell script that agents and skills can invoke to: detect what tests the project has, run them, and emit structured instructions for the smoke test phase. The script is the deterministic half of the gate — it handles everything that can be verified by exit code.

## External Behavior

**Location:** `skills/swain-test/scripts/swain-test.sh`, symlinked to `.agents/bin/swain-test.sh` during installation. Callers always use `.agents/bin/swain-test.sh`.

**Invocation:**
```bash
.agents/bin/swain-test.sh [--artifacts SPEC-NNN,SPEC-NNN]
```

**Inputs:**
- `--artifacts` (optional): comma-separated artifact IDs the agent considers relevant. Used to cross-reference artifact folders.
- Implicit: git state of the repository (diff, changed files, project structure files).

**Changed file detection:**
- In a worktree (HEAD differs from trunk): `git diff --name-only trunk..HEAD` + `git diff --name-only` (unstaged)
- On trunk directly: `git diff --name-only HEAD~1..HEAD` + `git diff --name-only` (unstaged)

**Test command detection (in order):**
1. `.agents/testing.json` `integration.command` — use if present
2. `package.json` present → `npm test`
3. `Cargo.toml` present → `cargo test`
4. `pyproject.toml` with `[tool.pytest]` section, or `pytest` in `requirements.txt` → `pytest`
5. `go.mod` present → `go test ./...`
6. `Makefile` with `test` target → `make test`
7. No match → skip integration phase, emit note

**Default timeout:** 120 seconds for convention-detected commands. `.agents/testing.json` `integration.timeout` overrides.

**Exit codes:**
- `0` — integration tests passed (or skipped); smoke instructions written to stdout
- `1` — integration tests failed; failure details written to stdout

**Stdout on exit 0:**
Structured sections for the agent to consume:
```
## INTEGRATION
status: PASS
command: pytest
duration: 12s
tests: 47/47

## ARTIFACTS
paths:
  - docs/spec/Active/(SPEC-NNN)-Title/(SPEC-NNN)-Title.md

## SKILLS
detected: true
changed_skill_files:
  - skills/swain-test/SKILL.md

## SMOKE
- start the dev server and verify the health endpoint returns 200

## FALLBACK
Describe what you changed, stand up the affected component, and exercise the happy path. Report what you did and what you observed.
```

The `ARTIFACTS` section lists file paths (not parsed ACs) so the agent reads the spec files and derives smoke steps from their acceptance criteria. The `SKILLS` section flags behavioral verification needed. The `SMOKE` section lists standing project smoke tests from `.agents/testing.json`. `FALLBACK` is emitted when `ARTIFACTS`, `SKILLS`, and `SMOKE` are all empty.

**Stdout on exit 1:**
```
## INTEGRATION
status: FAIL
command: pytest
output: [truncated test failure output, last 50 lines]
```

## Acceptance Criteria

**Given** the script is invoked in a project with `package.json`,
**When** `npm test` exits 0,
**Then** the script exits 0 and stdout contains `status: PASS` in the `## INTEGRATION` section.

**Given** the script is invoked in a project with `package.json`,
**When** `npm test` exits non-zero,
**Then** the script exits 1 and stdout contains `status: FAIL` with the last 50 lines of test output.

**Given** the script is invoked with `--artifacts SPEC-215`,
**When** exit is 0,
**Then** stdout contains a `## ARTIFACTS` section with the resolved path to SPEC-215's folder file.

**Given** the changed file list includes a file under `skills/`,
**When** exit is 0,
**Then** stdout contains `## SKILLS` with `detected: true` and the changed skill file listed.

**Given** no test command is detected and no `.agents/testing.json` exists,
**When** invoked,
**Then** the script exits 0, notes the skip in `## INTEGRATION`, and emits `## FALLBACK` instructions.

**Given** `.agents/testing.json` declares `integration.command: "pytest -v"` and `integration.timeout: 300`,
**When** invoked,
**Then** the script uses `pytest -v` with a 300-second timeout instead of convention detection.

**Given** the repository HEAD is on trunk (not a worktree branch),
**When** invoked,
**Then** the script uses `git diff --name-only HEAD~1..HEAD` for changed file detection.

## Scope & Constraints

- The script does not parse markdown or extract ACs from spec files — it emits paths only.
- The script does not orchestrate Phase 2 — it only produces instructions for the agent.
- The script does not modify any files — it is read-only except for stdout.
- The script must complete Phase 1 within the configured timeout (default 120s).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
