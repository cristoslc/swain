# swain-do Completion Chain Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a completion pipeline to swain-do's plan-completion handler so BDD, smoke, and retro run automatically when all tasks close — no manual sequencing.

**Architecture:** Insert a new Step 2 (completion pipeline) and renumber existing steps (old 2→3, old 3→4) in `skills/swain-do/SKILL.md`. The pipeline creates `.agents/completion-state.json` per DESIGN-018, then runs BDD, smoke, and retro in sequence. Each sub-step updates the state file atomically. Step 3 (SPEC transition) is gated on pipeline completion.

**Tech Stack:** Markdown (skill file), bash (inline code blocks), jq (state file operations)

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `skills/swain-do/SKILL.md` | Modify (lines 226-275) | Add completion pipeline section between Step 1 and Step 2 |

This is a single-file change. The SKILL.md is agent behavioral guidance written in markdown — no scripts, no tests. The "code" is the bash snippets inside fenced code blocks that agents copy-paste when following the skill instructions.

---

## Chunk 1: Completion Pipeline

### Task 1: Add completion state file creation block

**Files:**
- Modify: `skills/swain-do/SKILL.md:239` (after the `OPEN_COUNT == 0` proceed line)

- [ ] **Step 1: Read the current Step 1 ending**

Read `skills/swain-do/SKILL.md` lines 230-240. Confirm the last line of Step 1 is:
```
If `OPEN_COUNT > 0`, the plan is not complete — continue working or ask the operator. If `OPEN_COUNT == 0`, proceed.
```

- [ ] **Step 2: Insert new section header and state file creation**

After line 239 (`If OPEN_COUNT...proceed.`), insert this new section:

````markdown

### Step 2 — Run completion pipeline (SPEC-257)

After detecting plan completion, run the quality gate pipeline before transitioning the SPEC. This ensures BDD tests, smoke tests, and retro all fire automatically.

#### 2a — Create completion state file

Identify the SPEC ID from the plan epic's `--external-ref`:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SPEC_ID=$(tk show <epic-id> 2>/dev/null | grep -i 'external_ref' | awk '{print $NF}')
if [ -z "$SPEC_ID" ]; then
  echo "ERROR: No SPEC linked to plan epic — cannot create completion state."
  # Fall through to Step 2 without the pipeline
fi
```

If `SPEC_ID` is empty, skip Step 2 entirely and proceed to Step 2. Log a warning.

Create the state file per DESIGN-018:

```bash
mkdir -p "$REPO_ROOT/.agents"
jq -n --arg spec "$SPEC_ID" --arg branch "$(git branch --show-current)" \
  '{spec_id: $spec, branch: $branch, pipeline_started: (now | todate), steps: {bdd_tests: {status: "pending", timestamp: null, detail: null}, smoke_test: {status: "pending", timestamp: null, detail: null}, retro: {status: "pending", timestamp: null, detail: null}}}' \
  > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```
````

- [ ] **Step 3: Verify the edit**

Read the file around the insertion point. Confirm the new `### Step 2` heading appears after Step 1's closing paragraph and before Step 2.

- [ ] **Step 4: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 add completion state file creation to plan completion"
```

---

### Task 2: Add BDD test gate step

**Files:**
- Modify: `skills/swain-do/SKILL.md` (append to Step 2 section)

- [ ] **Step 1: Read the end of Task 1's insertion**

Confirm the state file creation block ends with the `mv` command inside a code fence.

- [ ] **Step 2: Append the BDD test gate block**

After the state file creation code block, append:

````markdown

#### 2b — Run BDD tests

Check if `swain-test.sh` is available:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SWAIN_TEST="$REPO_ROOT/.agents/bin/swain-test.sh"
```

**If `swain-test.sh` exists:** Run it once, capture output and exit code:

```bash
BDD_OUTPUT=$(bash "$SWAIN_TEST" --artifacts "$SPEC_ID" 2>&1)
BDD_EXIT=$?
```

- If exit code is 0 → update state to `passed`:
  ```bash
  BDD_DETAIL=$(echo "$BDD_OUTPUT" | head -5 | tr '\n' ' ')
  jq --arg status "passed" --arg detail "$BDD_DETAIL" \
    '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
    "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
    && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
  ```
- If exit code is non-zero → update state to `failed`:
  ```bash
  BDD_DETAIL=$(echo "$BDD_OUTPUT" | tail -10 | tr '\n' ' ')
  jq --arg status "failed" --arg detail "$BDD_DETAIL" \
    '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
    "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
    && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
  ```
  Stop the pipeline. Report the failure to the operator: "BDD tests failed. Details: {detail}. Say **retry** to re-run, or **skip BDD** to continue without."

**If `swain-test.sh` does not exist:** Warn and mark skipped:

```bash
jq --arg status "skipped" --arg detail "swain-test.sh not available" \
  '.steps.bdd_tests.status = $status | .steps.bdd_tests.timestamp = (now | todate) | .steps.bdd_tests.detail = $detail' \
  "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```

Display: "swain-test not available — skipping BDD gate."
````

- [ ] **Step 3: Verify the edit**

Read the section. Confirm 2b follows 2a and the code blocks use the atomic write pattern (write to `.tmp`, then `mv`).

- [ ] **Step 4: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 add BDD test gate to completion pipeline"
```

---

### Task 3: Add smoke test step

**Files:**
- Modify: `skills/swain-do/SKILL.md` (append to Step 2 section)

- [ ] **Step 1: Read the end of Task 2's insertion**

Confirm 2b ends with the "swain-test not available" fallback block.

- [ ] **Step 2: Append the smoke test block**

After 2b, append:

````markdown

#### 2c — Run smoke tests

Only proceed if `bdd_tests` is `passed` or `skipped`. If `bdd_tests` is `failed`, the pipeline is paused — do not run smoke.

```bash
BDD_STATUS=$(jq -r '.steps.bdd_tests.status' "$REPO_ROOT/.agents/completion-state.json")
```

If `BDD_STATUS` is `passed` or `skipped`:

**If `swain-test.sh` exists:** The smoke test output from `swain-test.sh` includes a `## SMOKE` section with manual verification steps. Present these to the operator and ask for confirmation:

> Smoke test instructions from swain-test:
> {smoke section content}
>
> Did the smoke test pass? (yes / no / skip)

- **yes** → update `smoke_test` to `passed` with detail "operator confirmed"
- **no** → update `smoke_test` to `failed` with detail from operator. Stop pipeline: "Smoke test failed. Say **retry** to re-check, or **skip smoke** to continue."
- **skip** → update `smoke_test` to `skipped` with detail "operator chose to skip"

Use the same jq update pattern from 2b to write state.

**If `swain-test.sh` does not exist:** Mark skipped with detail "swain-test.sh not available", same as BDD fallback.
````

- [ ] **Step 3: Verify the edit**

Read the section. Confirm 2c follows 2b and references the correct state keys.

- [ ] **Step 4: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 add smoke test step to completion pipeline"
```

---

### Task 4: Add retro step

**Files:**
- Modify: `skills/swain-do/SKILL.md` (append to Step 2 section)

- [ ] **Step 1: Read the end of Task 3's insertion**

Confirm 2c ends with the smoke test fallback block.

- [ ] **Step 2: Append the retro step block**

After 2c, append:

````markdown

#### 2d — Run retrospective

Only proceed if both `bdd_tests` and `smoke_test` are `passed` or `skipped`. Retro **cannot be skipped** — if the operator says "skip retro", refuse: "Retro always runs. It captures learning even from imperfect work."

Invoke the swain-retro skill using the agent's Skill tool (this is a tool invocation, not a bash command):

> Use the **Skill** tool: invoke `swain-retro` with args: `"SPEC completion — run retro for <SPEC-ID> before phase transition."`

After swain-retro completes, update the state:

```bash
jq --arg status "passed" --arg detail "retro captured" \
  '.steps.retro.status = $status | .steps.retro.timestamp = (now | todate) | .steps.retro.detail = $detail' \
  "$REPO_ROOT/.agents/completion-state.json" > "$REPO_ROOT/.agents/completion-state.json.tmp" \
  && mv "$REPO_ROOT/.agents/completion-state.json.tmp" "$REPO_ROOT/.agents/completion-state.json"
```

If swain-retro fails (skill invocation error), update state to `failed` and report. The operator can say **retry** to re-run.
````

- [ ] **Step 3: Verify the edit**

Read the section. Confirm 2d follows 2c and includes the "cannot be skipped" rule.

- [ ] **Step 4: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 add retro step to completion pipeline"
```

---

### Task 5: Add skip and resume handling

**Files:**
- Modify: `skills/swain-do/SKILL.md` (append to Step 2 section)

- [ ] **Step 1: Append skip and resume guidance to Step 2**

After the 2d retro section (after "The operator can say **retry** to re-run."), append this as a new sub-section:

````markdown

#### 2e — Skip and resume handling

**Skip handling:** At any point during the pipeline, the operator can say:
- "skip BDD" → set `bdd_tests` to `skipped` with detail "operator requested skip", continue to 2c
- "skip smoke" → set `smoke_test` to `skipped` with detail "operator requested skip", continue to 2d
- "skip retro" → **refuse**. Retro always runs. Say: "Retro captures learning even from imperfect work — it cannot be skipped."

**Resume handling:** If a step failed and the operator says "retry" or "continue":
1. Read `.agents/completion-state.json`
2. Find the first step with status `pending` or `failed`
3. Resume the pipeline from that step — do not re-run steps that already `passed` or were `skipped`

**Pipeline gate:** After all three steps, verify completion:

```bash
PENDING=$(jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$REPO_ROOT/.agents/completion-state.json")
```

If `PENDING` is empty (all steps `passed` or `skipped`), proceed to Step 2 (SPEC transition). If not, the pipeline is blocked — report which steps remain.
````

- [ ] **Step 2: Verify the edit**

Read the full Step 2 section. Confirm sub-sections 2a through 2e are present and logically ordered.

- [ ] **Step 3: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 add skip/resume handling to completion pipeline"
```

---

### Task 6: Renumber existing steps and add pipeline gate

**Files:**
- Modify: `skills/swain-do/SKILL.md` (existing Step 2 and Step 3 headings + content)

The new pipeline is Step 2. The existing steps need renumbering:
- Old "Step 2 �� Invoke swain-design" → **Step 3**
- Old "Step 3 — Offer merge and cleanup" → **Step 4**

- [ ] **Step 1: Renumber the old Step 2 heading**

Change:
```
### Step 2 — Invoke swain-design for SPEC transition
```
to:
```
### Step 3 — Invoke swain-design for SPEC transition
```

- [ ] **Step 2: Renumber the old Step 3 heading**

Change:
```
### Step 3 — Offer merge and cleanup
```
to:
```
### Step 4 — Offer merge and cleanup
```

- [ ] **Step 3: Add pipeline gate to Step 3's intro**

Before the existing Step 3 content (the `tk show` command), add this gate paragraph:

```markdown
**Pipeline gate (SPEC-257):** Only proceed to SPEC transition if the completion pipeline passed. Check: `jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$REPO_ROOT/.agents/completion-state.json"`. If any steps are `pending` or `failed`, do not transition — return to Step 2 to resolve.
```

- [ ] **Step 4: Update Step 3's retro reference**

The current text says:
> If the EPIC reaches a terminal state → invokes **swain-retro** to capture the retrospective

Update to clarify the EPIC-level retro is separate from the SPEC-level retro in Step 2d:

Change:
```
- If the EPIC reaches a terminal state → invokes **swain-retro** to capture the retrospective
```
to:
```
- If the EPIC reaches a terminal state → invokes **swain-retro** for the EPIC-level retrospective (the SPEC-level retro already ran in Step 2d)
```

- [ ] **Step 5: Verify all steps in order**

Read the full "Plan completion and handoff" section. Verify this order:
1. Step 1 — Detect plan completion
2. Step 2 — Run completion pipeline (2a–2e)
3. Step 3 — Invoke swain-design for SPEC transition (with pipeline gate)
4. Step 4 — Offer merge and cleanup

- [ ] **Step 6: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 renumber steps, gate SPEC transition on completion pipeline"
```

---

### Task 7: Update "Skipping the chain" section

**Files:**
- Modify: `skills/swain-do/SKILL.md` (existing "Skipping the chain" section)

- [ ] **Step 1: Read the current "Skipping the chain" section**

It currently says the operator can bypass steps 2-3. This needs to mention the completion pipeline too.

- [ ] **Step 2: Update the section**

Change:
```markdown
### Skipping the chain

The operator can say "just exit" or "skip the handoff" to bypass steps 2–3 and go directly to `ExitWorktree`. Log a note on the plan epic: `tk add-note <epic-id> "Exited worktree without completion handoff"`.
```

to:

```markdown
### Skipping the chain

The operator can say "just exit" or "skip the handoff" to bypass Steps 2–4 and go directly to `ExitWorktree`. Log a note on the plan epic: `tk add-note <epic-id> "Exited worktree without completion handoff"`.

**Note:** Skipping the chain means the completion pipeline did not run. If `.agents/completion-state.json` was already created (Step 2a ran), any `pending` steps remain pending. swain-teardown will detect this and invoke the missing steps before sync.
```

- [ ] **Step 3: Verify the edit**

Read the section. Confirm it references Step 2 and mentions teardown as the safety net.

- [ ] **Step 4: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): SPEC-257 update skip-chain to mention completion pipeline"
```

---

### Task 8: Final verification

- [ ] **Step 1: Read the full "Plan completion and handoff" section**

Read `skills/swain-do/SKILL.md` from `## Plan completion and handoff` to `## Fallback`. Verify:
- Step 1 (detect) is unchanged
- Step 2 (completion pipeline) has sub-sections 2a through 2e
- Step 3 (SPEC transition) has the pipeline gate paragraph and updated retro reference
- Step 4 (merge and cleanup) is unchanged except the heading number
- "Skipping the chain" references Steps 2–4

- [ ] **Step 2: Verify DESIGN-018 alignment**

Check that the state file schema in Step 2a matches DESIGN-018. Expected schema: `{spec_id, branch, pipeline_started, steps: {bdd_tests, smoke_test, retro}}` where each step has `{status, timestamp, detail}`. Verify:
- Has `spec_id`, `branch`, `pipeline_started` at top level
- Has `steps.bdd_tests`, `steps.smoke_test`, `steps.retro`
- Each step has `status`, `timestamp`, `detail`
- Uses atomic writes (`.tmp` + `mv`)

- [ ] **Step 3: Verify AC coverage**

| AC | Covered by |
|----|-----------|
| AC-1 (creates state file) | Task 1, Step 2a |
| AC-2 (runs BDD) | Task 2, Step 2b |
| AC-3 (runs smoke) | Task 3, Step 2c |
| AC-4 (runs retro) | Task 4, Step 2d |
| AC-5 (resume from failed) | Task 5, Step 2e resume handling |
| AC-6 (skip BDD/smoke) | Task 5, Step 2e skip handling |
| AC-7 (retro cannot skip) | Task 4, Step 2d + Task 5, Step 2e |
| AC-8 (all done → transition) | Task 6, pipeline gate |

- [ ] **Step 4: Final commit (if any fixups needed)**

```bash
git add skills/swain-do/SKILL.md
git commit -m "fix(swain-do): SPEC-257 fixups from verification pass"
```
