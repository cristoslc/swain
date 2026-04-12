---
name: swain-test
description: Test gate for swain-sync and swain-release — runs integration tests and emits smoke instructions
version: 1.0.0
---

# swain-test

Automated two-phase test gate. Phase 1 runs deterministic integration tests via `swain-test.sh`. Phase 2 runs agent-driven smoke tests that verify observable behavior against spec acceptance criteria, changed skills, and project-declared smoke items.

The gate is invoked by `swain-sync` before committing and by `swain-release` before cutting a release. Agents may also invoke it directly when they want to verify work before declaring completion.

## Inputs

- `--artifacts SPEC-NNN[,SPEC-NNN...]` — optional comma-separated list of artifact IDs the agent considers relevant to the current work. The gate resolves these to file paths and uses them to drive Phase 2 spec-derived verification.

If the agent is unsure which artifacts apply, they should pass the IDs from recent commits, the active focus lane, and any spec tags on tickets claimed during the work.

## Phase 1 — Integration tests (script-driven)

1. Invoke the integration script:
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
   bash "$REPO_ROOT/.agents/bin/swain-test.sh" --artifacts "$ARTIFACT_IDS"
   ```
2. Read the script's exit code:
   - **exit 1** — integration tests failed. Report the failure output to the operator. Fix the issue, re-stage any edits, and re-invoke the gate from Phase 1. Do not proceed to Phase 2.
   - **exit 0** — integration tests passed or were skipped. Read stdout and proceed to Phase 2.
3. Parse the script's stdout. It emits these sections:
   - `## INTEGRATION` — always present. Shows the command, status, duration, and (on failure) output tail.
   - `## ARTIFACTS` — present when `--artifacts` was passed and IDs resolved. Lists spec paths.
   - `## SKILLS` — present when files under `skills/`, `.agents/skills/`, or `.claude/skills/` changed in the branch. Lists changed skill files.
   - `## SMOKE` — present when `.agents/testing.json` declares smoke items.
   - `## FALLBACK` — present only when none of the above context sections appeared.

## Phase 2 — Smoke tests (agent-executed)

Execute the sections in the order below. Skip any section that was not emitted.

### Step 1 — Spec-derived verification (`## ARTIFACTS`)

For each spec path listed:

1. Read the spec file.
2. Locate the Acceptance Criteria section.
3. For each acceptance criterion, exercise the relevant component and observe the outcome. Write a short evidence line per criterion: what was done, what was observed, pass or fail.
4. If a criterion cannot be exercised (e.g., external dependency unavailable), record that explicitly rather than silently skipping.

### Step 2 — Behavioral verification (`## SKILLS`)

When `## SKILLS` shows `detected: true`:

1. For each changed skill file, dispatch a subagent with a representative prompt that should trigger the skill. The haiku model is recommended for cost; the choice is not required.
2. Observe whether the skill activates and produces the expected output.
3. Record: the prompt used, whether activation was confirmed, a short summary of the output.

The goal is not exhaustive coverage — one representative prompt per changed skill is enough to catch structural regressions (broken frontmatter, missing required sections, wrong file path).

### Step 3 — Standing smoke tests (`## SMOKE`)

Each smoke entry in `.agents/testing.json` is a declarative instruction. Execute each as an agentic task and record the result.

### Step 4 — Fallback (`## FALLBACK`)

If `## ARTIFACTS`, `## SKILLS`, and `## SMOKE` were all absent, follow the fallback instruction:

1. Describe what changed in the working tree.
2. Stand up the affected component (run the script, start the server, invoke the function).
3. Exercise the happy path.
4. Report what was observed.

## Failure handling

- **Any Phase 2 failure** — fix the issue, re-stage, and re-invoke the full gate from Phase 1. Never resume Phase 2 mid-flight; the Phase 1 re-run confirms that fixes did not break integration tests.
- **Two failed full-gate attempts** — do not attempt a third fix. Escalate to the operator with a structured report: every failure observed, every fix attempted, the observable state after each attempt. The two-strike rule prevents runaway repair loops that consume tokens without converging.
- **Operator override** — the operator can bypass the gate by stating a reason. Record the override verbatim in the evidence summary as `operator override: <reason>` and in the commit message when the work is committed.

## Evidence summary

After the gate passes (or is overridden), produce a structured evidence summary for downstream consumers (SPEC-226 evidence recording, retros, commit messages). Include:

- Phase 1 status (PASS / FAIL / SKIP) and command.
- For each Phase 2 step executed: which section drove it, what was done, what was observed, pass or fail.
- Any overrides and their reasons.

## Example flow

```
Agent: invokes swain-test.sh --artifacts SPEC-220
Script: exits 0, emits ## INTEGRATION (PASS), ## ARTIFACTS (SPEC-220 path), ## SKILLS (detected: true)
Agent (Step 1): reads SPEC-220, exercises each AC, records evidence.
Agent (Step 2): dispatches haiku subagent with a prompt that should trigger the changed skill; confirms activation.
Agent (Step 4): no ## FALLBACK section emitted; step skipped.
Agent: writes evidence summary.
```
