---
title: "Verification evidence recording"
artifact: SPEC-226
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: medium
type: feature
parent-epic: EPIC-052
parent-initiative: ""
linked-artifacts:
  - EPIC-052
  - SPEC-221
depends-on-artifacts:
  - SPEC-221
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Verification evidence recording

## Problem Statement

After swain-test runs, the evidence lives only in the conversation. The operator cannot look back at what was tested on a prior merge without reading conversation history. Evidence must travel with the code: in artifact folders and in the git commit message.

## Desired Outcomes

Every gate run produces two persistent records: a `verification-log.md` entry in each relevant artifact folder, and a short annotation in the commit message. Both survive session end and are readable without conversation context.

## External Behavior

**Verification log format:**
Each artifact folder that was part of the gate run gets a `verification-log.md`. If the file doesn't exist, create it. Append one entry per gate run — never overwrite.

```markdown
## 2026-03-31 — swain-sync pre-push

### Integration tests
- Command: `pytest -v`
- Result: PASS (47 tests, 0 failures)
- Duration: 12s

### Smoke tests
- SPEC-220: Invoked script from consumer worktree → exit 0, PASS section emitted correctly
- SPEC-221: Dispatched haiku subagent with prompt "run the test gate" → skill activated, emitted Phase 1 + 2 instructions
- Standing: Ran `make test` → 12 tests, all pass
- Behavioral: swain-test SKILL.md changed → subagent activated, correct routing confirmed

### Outcome: PASS
```

When the gate covers multiple artifact IDs, each artifact's `verification-log.md` gets the full entry. Evidence is duplicated, not split — a reader can understand any single artifact's history without cross-referencing others.

**Operator override format:**
```markdown
### Outcome: OPERATOR OVERRIDE
Reason: smoke tests skipped — component requires external service not available in CI
```

**Commit message annotation:**
After the gate passes, append a one-line `Verified:` annotation to the commit message before push:

```
Verified: integration PASS (pytest, 47/47), smoke PASS (3 checks)
```

For skipped integration:
```
Verified: integration skipped (no tests detected), smoke PASS (fallback — described hello-world CLI invocation)
```

For operator override:
```
Verified: operator override — smoke tests skipped (external service unavailable)
```

**When no artifacts are provided:**
If `--artifacts` was not passed to swain-test.sh and no artifact IDs can be inferred from context, record evidence only in the commit message annotation. No `verification-log.md` is written.

## Acceptance Criteria

**Given** a gate run passes with artifact IDs SPEC-220 and SPEC-221,
**When** evidence is recorded,
**Then** both `docs/spec/Active/(SPEC-220)-*/verification-log.md` and `docs/spec/Active/(SPEC-221)-*/verification-log.md` contain the full gate entry with integration and smoke results.

**Given** a `verification-log.md` already exists in an artifact folder,
**When** a new gate run completes,
**Then** the new entry is appended at the top (newest first) and the existing content is preserved.

**Given** a gate passes with integration tests and 2 smoke checks,
**When** the commit message is assembled,
**Then** it includes `Verified: integration PASS (command, N/N), smoke PASS (2 checks)`.

**Given** integration tests were skipped (no command detected),
**When** the commit message is assembled,
**Then** it includes `Verified: integration skipped (no tests detected)`.

**Given** the operator overrides the gate,
**When** evidence is recorded,
**Then** the log entry notes `OPERATOR OVERRIDE` and includes the stated reason, and the commit message includes `operator override`.

## Scope & Constraints

- Evidence recording runs after gate success (or operator override) only — never on failure.
- Logs are append-only — never modify or delete existing entries.
- If an artifact folder does not exist (e.g., flat file artifact), skip that artifact's log and note the skip. Do not fail the gate over a missing folder.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation; renumbered from SPEC-222 due to untracked collision |
