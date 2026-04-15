# Comprehensive Audit Sweep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the two-phase audit+fix run described in `docs/superpowers/specs/2026-04-12-comprehensive-audit-design.md`, landing all non-deferred fixes on `master`.

**Architecture:** Single agentrc run `comprehensive-audit`. Phase 1 spawns six parallel reader auditors that emit findings docs via `agentrc worker result`; orchestrator commits on `orc/audit-reports` and merges after a review panel. Phase 2 spawns one writer bucket per (domain, severity) pair after a human-approved triage; each bucket passes the REVIEW GATE before merging with `git merge --no-ff`.

**Tech Stack:** agentrc CLI (Rust, in-repo), tmux panes, git worktrees, Claude Code workers with subagent dispatch (`voltagent-*` families), `cargo fmt && cargo build && cargo test` as the verification harness.

**Executor:** the orchestrator Claude Code session. This plan is a runbook the orchestrator follows; most tasks are orchestrator actions rather than code edits. Worker sessions (spawned by `agentrc spawn`) follow the briefs the orchestrator writes in Phase 0.

---

## Phase 0 — Setup

### Task 0.1: Pre-flight environment check

**Files:** none (verification only).

- [ ] **Step 1: Check `.orchestrator/` exists and no active run is already running.**

Run: `agentrc status --json | head -20`
Expected: either "no active run" or an archived run. If an active run exists, stop and ask the user whether to archive it before proceeding.

- [ ] **Step 2: Confirm `max_workers` is ≥ 6.**

Run: `cat .orchestrator/config.json | grep max_workers`
Expected: `"max_workers": 12` (project default). If < 6, edit the file to bump to at least 6 before spawning.

- [ ] **Step 3: Verify the ten specialist-subagent namespaces are available.**

Subagents referenced: `voltagent-qa-sec:qa-expert`, `voltagent-qa-sec:test-automator`, `voltagent-qa-sec:security-auditor`, `voltagent-qa-sec:code-reviewer`, `voltagent-qa-sec:performance-engineer`, `voltagent-dev-exp:refactoring-specialist`, `voltagent-biz:product-manager`, `voltagent-biz:technical-writer`, `voltagent-lang:rust-engineer`, `voltagent-qa-sec:architect-reviewer`.

Check availability by inspecting the Agent tool's `subagent_type` list in the current session (the system message lists available agent types at session start). For each missing namespace, record a substitution before spawning:
- `voltagent-biz:product-manager` → `voltagent-biz:business-analyst`
- `voltagent-biz:technical-writer` → `voltagent-biz:content-marketer`
- `voltagent-dev-exp:refactoring-specialist` → `voltagent-qa-sec:code-reviewer` (already used elsewhere; note the doubling)
- any other missing specialist → nearest voltagent-qa-sec or voltagent-lang equivalent

Substitutions are recorded in `.orchestrator/active/plan.md` before phase 1 launches.

- [ ] **Step 4: Verify the working tree is clean on `master`.**

Run: `git status --short && git rev-parse --abbrev-ref HEAD`
Expected: empty output and `master`. If not, stop and surface to the user.

### Task 0.2: Create the run and the audits directory

**Files:**
- Create: `.orchestrator/active/` (via `agentrc run create`)
- Create: `docs/audits/` (directory only — contents land in Phase 1)

- [ ] **Step 1: Create the agentrc run.**

Run: `agentrc run create --slug comprehensive-audit`
Expected: stdout prints the new run id (e.g., `20260412T170000-comprehensive-audit`). Verify with `readlink .orchestrator/active` — should resolve to `runs/<id>/`. `agentrc status` shows 0 tasks.

- [ ] **Step 2: Create the audits directory.**

Run: `mkdir -p docs/audits && touch docs/audits/.gitkeep`
Expected: directory exists. The `.gitkeep` is a placeholder so the directory can be committed empty if phase 1 produces no findings (degenerate case).

- [ ] **Step 3: Checkpoint the run.**

Run: `agentrc checkpoint save -m "run created, phase 0 complete"`
Expected: checkpoint written.

### Task 0.3: Write the six Phase 1 audit briefs

**Files:**
- Create: `.orchestrator/active/tasks/001-audit-test-coverage.md`
- Create: `.orchestrator/active/tasks/002-audit-security.md`
- Create: `.orchestrator/active/tasks/003-audit-performance.md`
- Create: `.orchestrator/active/tasks/004-audit-code-quality.md`
- Create: `.orchestrator/active/tasks/005-audit-product-spec.md`
- Create: `.orchestrator/active/tasks/006-audit-rust-impl.md`

Each brief follows this template. Substitute the domain-specific fields.

- [ ] **Step 1: Write the common brief template with per-domain substitutions.**

Brief template (`{{domain}}`, `{{specialists}}`, `{{focus_list}}` substituted per task):

```markdown
---
id: "{{NNN}}"
slug: audit-{{domain}}
classification: reader
base_branch: master
pane_id: null
depends_on: []
created_at: 2026-04-12T00:00:00Z
---

# Phase 1 Audit — {{domain}}

You are a phase-1 reader auditor. You do **not** modify source files or run
git commands. You dispatch specialist subagents to produce findings and
emit a single findings document via `agentrc worker result`.

## Your model

Use `model: "opus"` on every Agent tool dispatch.

## Scope

Full `src/` and `tests/` trees. Exclude `target/`.

{{#if extra_docs}}
You additionally read: `docs/`, `README.md`, `CLAUDE.md`, `skill/agentrc/`.
{{/if}}

## Specialists to dispatch

{{specialists}}

Every Agent dispatch prompt MUST include: "Do NOT run any git commands.
Write/edit files only. I will handle all git operations."

## Focus

{{focus_list}}

## Finding schema (mandatory, every finding)

```markdown
## F-<NN>: <title>
- **Severity:** critical | high | medium | low
- **Location:** `path/to/file.rs:LINE` (or range)
- **Description:** what's wrong, one paragraph.
- **Proposed remediation:** concrete change.
- **Confidence:** high | medium | low
```

## Report structure

1. Front matter: domain, totals by severity, one-paragraph summary.
2. Full finding list ordered critical → high → medium → low, then by
   location for stable diffs.

## Output protocol

- Draft your findings doc in a scratch file: `/tmp/audit-{{NNN}}-findings.md`.
- When complete, emit via: `agentrc worker result --task {{NNN}} --file /tmp/audit-{{NNN}}-findings.md`. (The `--stdin` alternative accepts the doc on stdin; pick whichever fits your session.)
- Report progress via `agentrc worker note --task {{NNN}} --text "..."` as you work.
- Report completion via `agentrc worker done --task {{NNN}}`.

## Rules

- You do not commit. You do not create files outside `agentrc worker *`.
- You do not modify any source file in any worktree.
- You dispatch subagents; subagents also do not run git.
- You may re-dispatch the same specialist if the first pass missed
  something, but each dispatch must be scoped (no "audit the whole
  codebase" super-prompts — scope by module or concern).
```

- [ ] **Step 2: Fill per-domain fields.**

The six per-domain substitutions:

| NNN | domain | specialists | focus_list | extra_docs |
|---|---|---|---|---|
| 001 | test-coverage | `voltagent-qa-sec:qa-expert` + `voltagent-qa-sec:test-automator` | Coverage gaps; missing edge-case tests; untested error branches; integration vs unit balance; flaky patterns; test isolation; fixture hygiene | no |
| 002 | security | `voltagent-qa-sec:security-auditor` + `voltagent-qa-sec:code-reviewer` | Unsafe code blocks; path traversal via user input; tmux/shell injection in command construction; git-command argument handling; file locking races around `.orchestrator/`; trust boundary of the shared FS bus; sensitive data in logs | no |
| 003 | performance | `voltagent-qa-sec:performance-engineer` | Status aggregation hot path; event-log tailing allocation; dashboard render cost; unnecessary clones/`to_string`s; fs walks on every status tick; rate-limit correctness for animation | no |
| 004 | code-quality | `voltagent-qa-sec:code-reviewer` + `voltagent-dev-exp:refactoring-specialist` | Over-long files (flag files > 400 lines); duplication across commands; inconsistent error handling (`?` vs `unwrap` vs `expect`); clippy findings (run `cargo clippy -- -W clippy::pedantic`); naming consistency; module boundary leaks | no |
| 005 | product-spec | `voltagent-biz:product-manager` + `voltagent-biz:technical-writer` | README ↔ CLI command-surface drift; SKILL.md ↔ actual orchestrator behavior drift; CLAUDE.md ↔ code enforcement drift; missing user-facing docs for commands present in `src/commands/`; command names/flags that diverge from documented examples | yes |
| 006 | rust-impl | `voltagent-lang:rust-engineer` + `voltagent-qa-sec:architect-reviewer` | Idiomaticity of error types (`thiserror` usage, `AppError` surface); trait/lifetime use; any `unsafe`; `Cargo.toml` hygiene (unused deps, version ranges); feature-flag coherence; `src/lib.rs` public surface — what should be `pub(crate)`? | yes |

- [ ] **Step 3: Commit all six briefs in one commit.**

```bash
git add .orchestrator/active/tasks/00[1-6]-audit-*.md
git commit -m "chore(audit): write phase 1 audit briefs"
```

---

## Phase 1 — Audit run

### Task 1.1: Spawn all six auditors

**Files:** none (CLI only).

- [ ] **Step 1: Spawn 001–006 in sequence (spawn is fast; all six end up running in parallel).**

```bash
agentrc spawn 001
agentrc spawn 002
agentrc spawn 003
agentrc spawn 004
agentrc spawn 005
agentrc spawn 006
```

Expected: each command prints the pane id and confirms the worker is running. `agentrc status` shows six tasks in `spawning` or `in_progress`.

- [ ] **Step 2: Verify panes are healthy.**

Run: `agentrc status --json` — every task should have a non-null `pane_id` and a recent heartbeat (within 120s).

### Task 1.2: Monitor until all six complete

**Files:** none.

- [ ] **Step 1: Watch the dashboard and status until all six reach `completed`.**

Do not treat elapsed time as a failure signal (CLAUDE.md rule). Workers routinely take 10–20 minutes. Check every 15–20 minutes via `agentrc status`.

The ONLY warrants for attention: `state == failed`, OR `heartbeat_stale && pane_is_dead`. If a worker fails or dies and the pane is gone, surface to the user for confirmation before `agentrc respawn <id>` — no auto-redispatch.

- [ ] **Step 2: Each completion triggers collection of the result.**

When a worker completes:
- Read `.orchestrator/active/results/<id>.md` (the canonical path written by `agentrc worker result`; verified against `src/fs/run.rs`).
- Copy the content to `docs/audits/<domain>.md` in the main worktree, mapping task id → domain per the Phase 1 table (001 → test-coverage, 002 → security, 003 → performance, 004 → code-quality, 005 → product-spec, 006 → rust-impl).
- **Do NOT teardown yet.** Tearing down per-worker is deferred until `orc/audit-reports` merges (see Task 1.4).

### Task 1.3: Stage the six audit docs on `orc/audit-reports`

**Files:**
- Create: `docs/audits/test-coverage.md`
- Create: `docs/audits/security.md`
- Create: `docs/audits/performance.md`
- Create: `docs/audits/code-quality.md`
- Create: `docs/audits/product-spec.md`
- Create: `docs/audits/rust-impl.md`

- [ ] **Step 1: Confirm all six result files exist and are non-empty.**

Run: `ls -la docs/audits/*.md | wc -l`
Expected: 6 (plus the `.gitkeep` placeholder which will be removed).

- [ ] **Step 2: Remove the `.gitkeep` now that docs exist.**

```bash
rm docs/audits/.gitkeep
```

- [ ] **Step 3: Create the audit-reports branch.**

```bash
git checkout -b orc/audit-reports
git add docs/audits/*.md
git commit -m "docs(audit): phase 1 findings reports (6 domains)"
```

### Task 1.4: Phase 1 review panel and merge

**Files:** none beyond what was committed above.

- [ ] **Step 1: Dispatch the phase-1 review panel in parallel.**

Parallel Agent tool dispatches (single message with two tool calls):
- `voltagent-biz:technical-writer` — review each of the six `docs/audits/*.md` for report quality, clarity, and adherence to the finding schema.
- `voltagent-qa-sec:code-reviewer` — verify every `file:LINE` citation in every finding points at real code (spot-check ≥ 20% of findings per doc). Flag any hallucinated locations.

Both dispatches must include: "Do NOT run any git commands. Report findings; do not modify files."

- [ ] **Step 2: Apply blocking fixes.**

If either reviewer flags a blocking issue (schema violation, hallucinated citation, unclear finding): edit the doc directly on the `orc/audit-reports` branch, commit as a fixup. Re-dispatch only if the scope is large.

- [ ] **Step 3: Merge to master.**

```bash
git checkout master
git merge --no-ff orc/audit-reports -m "Merge branch 'orc/audit-reports' — reviewed"
```

Expected: six audit docs now on `master`.

- [ ] **Step 4: Teardown the six phase-1 panes.**

```bash
agentrc teardown 001
agentrc teardown 002
agentrc teardown 003
agentrc teardown 004
agentrc teardown 005
agentrc teardown 006
```

- [ ] **Step 5: Checkpoint.**

```bash
agentrc checkpoint save -m "phase 1 complete, reports merged"
```

---

## Phase 2 — Triage gate

### Task 2.1: Read and normalize findings

**Files:** none yet (orchestrator reasoning).

- [ ] **Step 1: Read all six audit docs.**

Read each `docs/audits/<domain>.md` in full. Build an internal list of every finding with domain tag, severity, location, description, remediation, and confidence.

- [ ] **Step 2: De-duplicate cross-domain findings.**

For each pair (A, B) where A.location == B.location and the descriptions overlap: merge into one finding, keep the stronger severity, concatenate domain tags (`security+code-quality`). Record the merge in the triage notes.

- [ ] **Step 3: Bucket by (primary domain, severity).**

For merged findings, the "primary domain" is the one with the stronger severity; ties broken by the priority order (security > perf > rust-impl > code-quality > test-coverage > product-spec).

### Task 2.2: Write `docs/audits/backlog.md`

**Files:**
- Create: `docs/audits/backlog.md`

- [ ] **Step 1: Write the backlog doc with every severity=low finding.**

Structure:

```markdown
# Audit Backlog — Deferred Low-Severity Findings

From the 2026-04-12 comprehensive audit sweep.

## From test-coverage
- F-NN: <title> — <one-line>

## From security
...
```

Include file:line for each so a future contributor can pick one up.

### Task 2.3: Write the Phase 2 fix plan

**Files:**
- Create: `.orchestrator/active/plan.md`

- [ ] **Step 1: Draft the DAG.**

One task per non-empty non-deferred-low bucket. Task ids start at `101`. Naming: `<task_id>-fix-<bucket>` (e.g., `101-fix-security-critical`).

Dependency rules:
1. Within a domain: higher severity must integrate before lower severity starts. Encode as `depends_on: ["<higher-severity-task-id>"]`.
2. Cross-domain file collisions identified during normalization: encode as `depends_on: ["<other-task-id>"]` with a note.
3. No other dependencies — buckets from different domains otherwise run in parallel.

Priority (for spawn ordering when `max_workers` is saturated): security > perf > rust-impl > code-quality > test-coverage > product-spec.

- [ ] **Step 2: Write the plan document.**

`.orchestrator/active/plan.md` structure:

```markdown
# Phase 2 Fix Plan

**Based on:** docs/audits/{test-coverage,security,performance,code-quality,product-spec,rust-impl}.md

## Buckets

| Task id | Bucket | Findings | Depends on | Primary specialist |
|---|---|---|---|---|
| 101 | security-critical | F-01, F-03 | — | rust-engineer + security-auditor |
| 102 | security-high | F-02, F-05, F-07 | 101 | rust-engineer + security-auditor |
| 103 | perf-high | F-11 | — | performance-engineer |
| ... | ... | ... | ... | ... |

## Deferred findings

Written to `docs/audits/backlog.md`. Not dispatched.

## Zero-bucket short-circuit

If no non-deferred buckets survive triage, phase 2 is skipped and the run archives with a "no remediation required" note.
```

- [ ] **Step 3: Commit backlog + plan together.**

```bash
git checkout -b orc/audit-triage
git add docs/audits/backlog.md .orchestrator/active/plan.md
git commit -m "docs(audit): triage — backlog + phase 2 fix plan"
git checkout master
git merge --no-ff orc/audit-triage -m "Merge branch 'orc/audit-triage' — triage landed"
```

Commit is on master before the HARD GATE so the deferred record is durable.

### Task 2.4: HARD GATE — user approves the plan

**Files:** none.

- [ ] **Step 1: Present the plan to the user.**

Show the bucket table, the total finding count per bucket, and the estimated worker count. Ask explicitly: "Approve the plan, modify buckets, or demote findings to backlog?"

- [ ] **Step 2: Apply approved changes.**

If the user modifies the plan, edit `.orchestrator/active/plan.md`, commit on a new `orc/audit-triage-amend` branch, run through the merge dance again.

- [ ] **Step 3: Do NOT proceed past this gate without explicit user approval.**

If plan has zero buckets → go to Task 4.1 (short-circuit completion).

---

## Phase 3 — Fix run

### Task 3.1: Write phase 2 briefs (one per approved bucket)

**Files:**
- Create: `.orchestrator/active/tasks/<task_id>-fix-<bucket>.md` × N (one per bucket)

- [ ] **Step 1: For each bucket, write the brief.**

Brief template:

```markdown
---
id: "{{task_id}}"
slug: fix-{{bucket}}
classification: writer
worktree: .orchestrator/active/worktrees/{{task_id}}
base_branch: master
branch: orc/{{task_id}}-fix-{{bucket}}
pane_id: null
depends_on: {{depends_on_list}}
created_at: 2026-04-12T00:00:00Z
---

# Phase 2 Fix — {{bucket}}

You are a writer worker. You own branch `orc/{{task_id}}-fix-{{bucket}}` in
worktree `.orchestrator/active/worktrees/{{task_id}}`.

## Your model

Use `model: "opus"` on every Agent tool dispatch.

## Findings to address

Exactly the following findings from the 2026-04-12 audit. For each: fix
with a test OR document as deferred-with-reason in your completion note.

{{verbatim_findings_list}}

## Specialists

Implementation: `{{primary_specialist}}` (e.g., `voltagent-lang:rust-engineer`).
Embedded review: `voltagent-qa-sec:security-auditor` at least once per
bucket.

Every Agent dispatch prompt MUST include: "Do NOT run any git commands.
Write/edit files only. I will handle all git operations."

## TDD contract

Every fix lands with a test.
- If the finding IS a missing-test finding, the new test IS the deliverable.
- For implementation fixes: write a failing test first demonstrating the
  defect, then implement, then watch it pass.

## Atomic edits rule

All edits → `cargo fmt && cargo build && cargo test` → single commit per
logical unit. Never commit between edits. Never commit a broken build.

## Completion criteria

Every finding is either:
1. Fixed with a test; referenced in a commit message, OR
2. Documented as deferred-with-reason in your `agentrc worker result`
   note. The orchestrator acks deferrals before teardown.

## Reporting

- `agentrc worker status --task {{task_id}} --state in_progress` on start.
- `agentrc worker note` for progress.
- `agentrc worker done --task {{task_id}}` on completion.
```

- [ ] **Step 2: Commit all briefs in one commit on master.**

Because briefs live in `.orchestrator/active/tasks/` (not source code), this is consistent with how phase-1 briefs landed. Prior runs in the repo follow the same pattern.

```bash
git add .orchestrator/active/tasks/1*-fix-*.md
git commit -m "chore(audit): write phase 2 fix briefs"
```

### Task 3.2: Spawn phase-2 writers in dependency order

**Files:** none.

- [ ] **Step 1: Spawn buckets with no unresolved dependencies.**

```bash
agentrc spawn 101    # e.g., security-critical
agentrc spawn 103    # perf-high — independent of 101
agentrc spawn 105    # rust-impl-high — independent
# etc. for every bucket with no `depends_on`
```

Respect priority ordering when `max_workers` is hit: security first, then perf, etc.

- [ ] **Step 2: Verify panes healthy.**

Run: `agentrc status --json` — each task should show `in_progress` with a fresh heartbeat.

### Task 3.3: Per-bucket review gate and merge

**Files:** none per bucket beyond the worker's branch.

For each bucket as it completes, repeat steps 1–5.

- [ ] **Step 1: Verify completion.**

Worker hits `completed`. Read the worker's final `result.md`. Confirm every finding in the bucket is either fixed (commit) or deferred (explicit note).

- [ ] **Step 2: Dispatch the REVIEW GATE in parallel.**

Minimum panel per skill:
- `voltagent-lang:rust-engineer` — diff review, idiomaticity, correctness.
- `voltagent-qa-sec:security-auditor` — security impact of the diff.

For perf buckets add `voltagent-qa-sec:performance-engineer`. For buckets touching module boundaries add `voltagent-qa-sec:architect-reviewer`. Up to 2 additional specialists permitted per the review-team rule in memory.

Each dispatch prompt: "Do NOT run any git commands. Review the diff at `orc/<task_id>-fix-<bucket>` vs master; report blockers and non-blockers. Do not modify files."

- [ ] **Step 3: Apply blocking fixes.**

If blockers: either (a) fix in-place on the bucket branch and re-run tests, or (b) surface to user for confirmation before respawn. Max 2 redispatches per bucket.

- [ ] **Step 4: Merge the bucket to master.**

```bash
git checkout master
git merge --no-ff orc/<task_id>-fix-<bucket> -m "Merge branch 'orc/<task_id>-fix-<bucket>' — reviewed"
cargo fmt && cargo build && cargo test
```

Expected: merge clean, all tests green. If tests fail post-merge, investigate before continuing — do not stack further merges on a broken master.

- [ ] **Step 5: Teardown and spawn unblocked dependents.**

```bash
agentrc teardown <task_id>
```

For any bucket whose `depends_on` list now has only integrated entries, `agentrc spawn <id>`.

- [ ] **Step 6: Checkpoint every few merges.**

```bash
agentrc checkpoint save -m "merged <task_id>-fix-<bucket>"
```

### Task 3.4: Collect deferred findings (if any)

**Files:**
- Create: `docs/audits/deferred-findings.md` (only if ≥ 1 deferred finding)

- [ ] **Step 1: Aggregate deferrals.**

For each bucket's completion note, extract every "deferred-with-reason" entry. If there are any, write `docs/audits/deferred-findings.md`:

```markdown
# Deferred Findings — 2026-04-12 Audit Sweep

These findings were in-scope for phase 2 but the assigned worker could not
reproduce or safely fix them. Revisit in a follow-up run.

## From bucket 101-fix-security-critical
- F-03: <title> — reason the worker deferred.
```

- [ ] **Step 2: Commit on its own branch, review, merge.**

Branch `orc/audit-deferred`, review panel = `voltagent-biz:technical-writer` + `voltagent-qa-sec:code-reviewer`, merge `--no-ff`.

---

## Phase 4 — Completion

### Task 4.1: Final summary

**Files:** none (reported to user; not committed).

- [ ] **Step 1: Produce the summary.**

Structure to deliver:
- Counts: findings discovered, findings fixed, findings deferred, findings backlogged.
- Per-bucket merge commits with SHAs.
- Link to `docs/audits/` (reports), `docs/audits/backlog.md`, `docs/audits/deferred-findings.md` (if present).
- Notable follow-ups worth a dedicated plan.

### Task 4.2: Archive the run

**Files:** `.orchestrator/` (managed by agentrc).

- [ ] **Step 1: Archive.**

```bash
agentrc run archive
```

Expected: `.orchestrator/active/` symlink updated to `.orchestrator/archived/<run-id>/`.

- [ ] **Step 2: Restore `max_workers` if bumped in Task 0.1.**

Edit `.orchestrator/config.json` back to its original value.

- [ ] **Step 3: Delete merged branches.**

List merged `orc/*` branches first, then delete.

```bash
git branch --merged master | grep '^  orc/' | grep -E 'audit|fix-' | xargs -r -n1 git branch -d
```

Expected: local `orc/*` audit branches pruned. Remote branches untouched (no push by any party per skill). If the grep matches nothing (all already deleted), command exits cleanly.

---

## Self-Review Checklist

After executing, confirm against the spec:

1. Six audit docs present under `docs/audits/` and on `master`.
2. Every non-deferred bucket merged to `master` with post-merge tests green.
3. `docs/audits/backlog.md` exists with low-severity findings.
4. `docs/audits/deferred-findings.md` exists IFF any worker deferred.
5. Run archived.
6. No `orc/*` audit branches linger.
7. `cargo build && cargo test` green on `master` at final state.
