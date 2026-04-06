---
title: "Completion Pipeline State Tracking"
artifact: DESIGN-018
track: standing
domain: system
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
superseded-by: ""
linked-artifacts:
  - EPIC-059
  - SPEC-257
  - SPEC-258
artifact-refs: []
sourcecode-refs: []
depends-on-artifacts: []
---

# Completion Pipeline State Tracking

## Design Intent

**Context:** swain-do and swain-teardown need a shared contract for tracking which post-completion steps have run for a given SPEC, so teardown can detect gaps and invoke missing steps.

### Goals
- A single structured file per worktree that records completion pipeline progress
- Each pipeline step is independently recorded with timestamp and pass/fail
- Both swain-do (writer) and swain-teardown (reader + writer) use the same format
- State survives session crashes — written incrementally, not at the end

### Constraints
- Must be a JSON file readable by bash scripts (jq) and agent skills
- Must live in the worktree, not in a global location — tied to the branch's work
- Must not require a running session to read (teardown may run after session close)

### Non-goals
- No historical aggregation across SPECs — this tracks one completion cycle
- No remote sync — this is local working state, not an artifact
- No UI or dashboard — skills read it directly

## Interface Surface

The completion pipeline state file tracks progress through the post-implementation quality gates for a single SPEC branch. It lives at `.agents/completion-state.json` in the worktree root.

## Contract Definition

### File location

`.agents/completion-state.json` — created by swain-do when all tasks close, read/updated by swain-teardown.

### Schema

```json
{
  "spec_id": "SPEC-123",
  "branch": "worktree-feature-name",
  "pipeline_started": "2026-04-04T21:00:00Z",
  "steps": {
    "bdd_tests": {
      "status": "passed",
      "timestamp": "2026-04-04T21:01:00Z",
      "detail": "14 scenarios, 14 passed"
    },
    "smoke_test": {
      "status": "passed",
      "timestamp": "2026-04-04T21:02:00Z",
      "detail": "operator confirmed"
    },
    "retro": {
      "status": "skipped",
      "timestamp": null,
      "detail": null
    }
  }
}
```

### Step statuses

| Status | Meaning |
|--------|---------|
| `pending` | Step not yet attempted |
| `running` | Step currently executing |
| `passed` | Step completed successfully |
| `failed` | Step ran but did not pass — needs attention |
| `skipped` | Step intentionally skipped by operator override |

### Step definitions

| Step key | What it does | Invoking skill |
|----------|-------------|----------------|
| `bdd_tests` | Run BDD acceptance tests via swain-test | swain-test |
| `smoke_test` | Run smoke tests or prompt operator for manual confirmation | swain-test |
| `retro` | Capture retrospective for the completed SPEC/EPIC | swain-retro |

### Operations

**Create** (swain-do, on plan completion):
```bash
jq -n --arg spec "$SPEC_ID" --arg branch "$(git branch --show-current)" \
  '{spec_id: $spec, branch: $branch, pipeline_started: (now | todate), steps: {bdd_tests: {status: "pending", timestamp: null, detail: null}, smoke_test: {status: "pending", timestamp: null, detail: null}, retro: {status: "pending", timestamp: null, detail: null}}}' \
  > .agents/completion-state.json
```

**Update step** (any skill, after running a step):
```bash
jq --arg step "$STEP" --arg status "$STATUS" --arg detail "$DETAIL" \
  '.steps[$step].status = $status | .steps[$step].timestamp = (now | todate) | .steps[$step].detail = $detail' \
  .agents/completion-state.json > .agents/completion-state.json.tmp \
  && mv .agents/completion-state.json.tmp .agents/completion-state.json
```

**Read pipeline status** (swain-teardown):
```bash
jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' .agents/completion-state.json
```

## Behavioral Guarantees

- File is created atomically (write to `.tmp`, then `mv`)
- Each step update is independent — a crash between steps leaves prior steps recorded
- Missing file means the completion pipeline was never started — teardown should create it and run all steps
- `skipped` status requires explicit operator override — skills never set it automatically

## Integration Patterns

- **swain-do** creates the file and runs steps in order (bdd_tests → smoke_test → retro)
- **swain-teardown** reads the file, identifies `pending` or `failed` steps, and invokes them
- **swain-test** updates `bdd_tests` and `smoke_test` steps after execution
- **swain-retro** updates the `retro` step after execution

## Evolution Rules

New steps can be added to the `steps` object without breaking existing readers — unknown keys are ignored. Step order is defined by the invoking skill, not by key order in JSON.

## Edge Cases and Error States

| Scenario | Behavior |
|----------|----------|
| File missing | Teardown creates it with all steps `pending` and runs them |
| Step fails | Status set to `failed` with detail; teardown re-attempts on next run |
| Session crash mid-pipeline | File persists with partial progress; teardown picks up remaining steps |
| Operator wants to skip a step | Must explicitly say "skip" — skill sets `skipped` status |
| Multiple SPECs in one worktree | Not supported — one completion-state per worktree. If multiple SPECs land in one worktree, track the last-completed SPEC |

## Design Decisions

- **JSON over YAML** — bash scripts need jq, which handles JSON natively. YAML would require yq as an extra dependency.
- **Flat step map over ordered array** — steps have known keys and independent status. A map is easier to update and query than an ordered list.
- **Worktree-local over global** — ties state to the branch where work happened. No cross-branch confusion.

## Assets

None — this is a data contract, not a visual design.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | 683a04e6 | Initial creation |
