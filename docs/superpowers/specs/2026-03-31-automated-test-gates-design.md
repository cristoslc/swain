# Automated Test Gates for swain-sync and swain-release

## Problem

The operator manually asks agents whether they've run integration tests and smoke tests before every worktree-to-trunk merge. Every time, this catches something that gets fixed before merge. This manual gate is effective but unsustainable — it relies on the operator remembering to ask, and it doesn't scale across sessions or projects.

## Solution

A new `swain-test` skill and backing script (`.agents/bin/swain-test.sh`) that enforces two-phase test verification as a hard gate in swain-sync and swain-release. The gate always runs. When a phase has nothing to execute (no tests detected, no smoke instructions generated), it passes with a "skipped — no tests configured" note rather than silently succeeding.

### Insertion points

- **swain-sync:** after commit (Step 5), before push (Step 6). The code is committed and in a runnable state. If the gate fails, the agent fixes and amends before pushing. On the worktree retry loop (Step 6 retries), the gate re-runs after each re-merge.
- **swain-release:** after security gate (Step 5.5) and README gate (Step 5.7), before tag creation (Step 6). All other gates pass first; test gate is the final check.
- **On trunk (no worktree):** the script uses `git diff --name-only HEAD~1..HEAD` plus unstaged changes instead of `trunk..HEAD`. The gate still runs — direct trunk commits deserve the same scrutiny.

## Script location

The script's canonical home is `skills/swain-test/scripts/swain-test.sh` (inside the swain-test skill directory). It is symlinked into `.agents/bin/swain-test.sh` during installation — the same pattern used by other swain scripts. Callers always invoke via `.agents/bin/swain-test.sh`; the symlink is maintained by `swain-doctor`.

## Architecture

```
swain-sync ──┐
             ├──▶ swain-test skill
swain-release┘        │
                      ├── Phase 1: Integration tests (deterministic, script-driven)
                      │     └── skills/swain-test/scripts/swain-test.sh
                      │         (symlinked → .agents/bin/swain-test.sh)
                      │           ├── git diff trunk..HEAD + dirty files → changed file list
                      │           ├── detect test command (convention or .agents/testing.json)
                      │           ├── run tests, report pass/fail
                      │           └── on pass: emit smoke test instructions to stdout
                      │
                      ├── Phase 2: Smoke tests (agent-executed, non-deterministic)
                      │     ├── agent follows instructions from script output
                      │     ├── spec-derived ACs first (from artifact IDs agent provides)
                      │     ├── standing project smoke tests second (.agents/testing.json)
                      │     ├── if skill files changed → behavioral verification via subagent
                      │     ├── generic fallback if no specific instructions available
                      │     └── collect evidence (what was done, what happened)
                      │
                      ├── Evidence recording
                      │     ├── append to artifact folder verification-log.md
                      │     └── annotate commit message
                      │
                      └── Failure handling
                            ├── fix and re-run full sequence
                            └── escalate to operator after 2 failures
```

## Phase 1: Integration tests

The script handles everything deterministic:

### Test command detection

1. If `.agents/testing.json` exists and has an `integration` field → use that command
2. Else detect from project files:
   - `package.json` → `npm test`
   - `Cargo.toml` → `cargo test`
   - `pyproject.toml` with `[tool.pytest]` section, or `pytest` in `requirements.txt` → `pytest`
   - `go.mod` → `go test ./...`
   - `Makefile` with `test` target → `make test`
3. If nothing detected → skip integration phase, proceed to smoke with a note

### Script inputs

```bash
swain-test.sh [--artifacts SPEC-213,SPEC-215]
```

- `--artifacts` is optional. The agent passes artifact IDs it knows are relevant — context the script can't derive from files alone.
- The script always runs `git diff --name-only trunk..HEAD` (or `HEAD~1..HEAD` when on trunk) plus `git diff --name-only` (unstaged) to build the changed-file list independently.
- Default timeout for convention-detected tests: 120 seconds. `.agents/testing.json` can override.

### Script output on integration pass

Structured instructions for the agent to follow in Phase 2. The script assembles these from:

1. **Spec-derived artifact paths** — cross-references artifact IDs (from `--artifacts` flag) against artifact folders, emits the file paths so the agent can read them and derive smoke steps from the acceptance criteria
2. **Skill detection** — if changed files include `*/SKILL.md` or files under `skills/`, `agents/skills/`, `.claude/skills/`, flags for behavioral verification via subagent
3. **Standing smoke tests** — appends `.agents/testing.json` `smoke` array entries if present
4. **Generic fallback** — if none of the above produce instructions: "Describe what you changed, stand up the affected component, and exercise the happy path. Report what you did and what you observed."

## Phase 2: Smoke tests

The agent executes the instructions emitted by the script. This is non-deterministic and token-expensive — it only runs after integration tests pass.

### Spec-derived verification (first)

For each artifact ID the agent provided, the agent exercises the acceptance criteria as verification steps. This is the most targeted form of smoke testing — it verifies the specific thing that was just built.

### Behavioral verification (when skills are present)

When the script detects skill file changes, the agent dispatches subagents (haiku recommended for cost, but model choice is up to the agent) with representative prompts to verify:
- The skill activates (correct routing)
- The output matches expected behavior
- Report: prompt used, whether skill activated, output summary

### Standing smoke tests (second)

Project-level tests from `.agents/testing.json` that should always pass regardless of what changed.

### Generic fallback

When no structured instructions are available, the agent must still produce evidence: what changed, what was stood up, what was exercised, what was observed.

## Evidence recording

### Artifact verification log

Each artifact folder gets a `verification-log.md` — append-only, one entry per gate run. When a gate run covers multiple artifacts, each artifact's log gets the full entry (evidence is duplicated, not split). The commit message annotation covers the aggregate.

```markdown
## 2026-03-31 — swain-sync pre-push

### Integration tests
- Command: `pytest -v`
- Result: PASS (47 tests, 0 failures)
- Duration: 12s

### Smoke tests
- SPEC-215: Ran test harness from consumer layout → TAP output 4/4 pass, exit 0
- Standing: Started dev server → health endpoint returned 200

### Outcome: PASS
```

### Commit message annotation

Short annotation appended to the commit message:

```
Verified: integration PASS (pytest, 47/47), smoke PASS (3 checks)
```

## Failure handling

- **Integration failure:** Agent fixes the issue, re-stages, and re-invokes the gate from the top (both phases). The gate is self-contained — it doesn't restart swain-sync's earlier steps (ADR compliance, collision detection, etc.). Those already passed.
- **Smoke/behavioral failure:** Agent fixes the issue, re-stages, and re-invokes the gate from the top. After 2 failed attempts, escalates to operator with evidence of what failed and what was tried.
- **Operator escape hatch:** Operator can override with an explicit statement. Override is recorded in verification log and commit message: "operator override: <reason>".

## Test configuration (optional)

`.agents/testing.json` format — most projects won't have this. Convention detection handles the common case.

```json
{
  "integration": {
    "command": "pytest -v",
    "timeout": 300
  },
  "smoke": [
    "start the dev server and verify the health endpoint returns 200",
    "run the CLI with --help and verify output lists all subcommands"
  ]
}
```

## Flat artifact migration

All artifact types must use folders (not flat files) so that `verification-log.md` has a home. One known flat file exists: `SPEC-183` in `docs/spec/Active/`. Templates must enforce folder structure going forward.

## Epic decomposition

| Spec | What | Depends on |
|------|------|-----------|
| swain-test.sh script | `.agents/testing.json` format, convention-based detection, integration test execution, smoke instruction assembly (artifact path resolution + skill detection + standing tests + fallback), structured stdout output | — |
| swain-test skill | Skill file: orchestrates both phases, agent smoke instructions, retry logic, escalation | swain-test.sh |
| Evidence recording | Verification log in artifact folders, commit message annotation | swain-test skill |
| swain-sync integration | Add gate invocation step after commit, before push | swain-test skill |
| swain-release integration | Add gate invocation step after README gate, before tag | swain-test skill |
| Flat artifact migration | Ensure all artifact types use folders + template enforcement | — |

SPEC-215 (consumer integration test harness) will be re-parented under this epic as a metadata update during epic creation.

## Out of scope

- `swain-init` / `swain-doctor` nudges to create `.agents/testing.json` — the gate works with convention detection
- Editing `finishing-a-development-branch` (superpowers, not ours)
- Test result caching across sessions
- Coverage metrics or reporting beyond pass/fail
- Concurrent worktree verification-log conflicts (unlikely; defer until observed)
- swain-do integration (test evidence doesn't feed back into task status — may revisit)
