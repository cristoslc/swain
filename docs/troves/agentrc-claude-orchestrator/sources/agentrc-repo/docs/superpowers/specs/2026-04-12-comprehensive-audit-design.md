# Comprehensive Audit Sweep — Design Spec

**Run slug:** `comprehensive-audit`
**Date:** 2026-04-12
**Status:** Design approved; implementation plan pending

## Purpose

Produce a full-spectrum audit of the `agentrc` codebase across six domains —
test coverage, security, performance, code quality, product spec alignment,
and Rust implementation idiomaticity — and land all non-deferred fixes on
`master` under the agentrc orchestration protocol.

The outcome of a successful run is:

1. Six findings documents checked in under `docs/audits/`.
2. All high/critical findings fixed with tests, merged to `master`.
3. Low-severity findings captured in `docs/audits/backlog.md` for follow-up.
4. The historical record of the sweep preserved via the run directory and
   merge commits.

## Terminology

- **Worker** — a Claude Code session running in its own tmux pane, spawned
  by `agentrc spawn <task_id>`. Identified by a 3-digit numeric `task_id`
  (e.g. `001`); the full brief filename is
  `.orchestrator/active/tasks/<task_id>-<slug>.md`.
- **Reader** — a worker whose brief classification is `reader`; does not
  get its own worktree or branch, runs in the main repo cwd, and does not
  commit. Output is emitted via `agentrc worker note` / `agentrc worker
  result` and persisted by the orchestrator.
- **Writer** — a worker with classification `writer`; gets an isolated
  git worktree on branch `orc/<task_id>-<slug>` and is the sole committer
  to that branch.
- **Bucket** — a (domain, severity) pair promoted into one phase-2 writer
  task: one branch, one worker, one review panel. Buckets are created
  dynamically from the findings that survive triage; empty buckets are
  never created.
- **REVIEW GATE** — the pre-merge multi-agent review required by
  `skill/agentrc/SKILL.md` before any branch is merged. Minimum panel:
  a stack specialist (`voltagent-lang:rust-engineer` for this codebase)
  plus `voltagent-qa-sec:security-auditor`, both dispatched in parallel
  with `model: "opus"`. Blocking findings must be addressed before
  `git merge --no-ff` runs.

See `skill/agentrc/SKILL.md` and `CLAUDE.md` for full protocol primitives.

## Architecture

One `agentrc` run, executed in two phases with a human-approved triage gate
between them.

```
Phase 1 (AUDIT)                Gate              Phase 2 (FIX)
──────────────────              ────              ───────────────
6 parallel reader workers   →  triage   →   N parallel writer workers
 - test-coverage             (orchestrator    (one per domain+severity
 - security                   reads all        bucket; each bucket =
 - performance                findings,        its own branch with
 - code-quality               proposes         own review panel)
 - product-spec               fix DAG,
 - rust-impl                  user
                              approves)
  ↓
docs/audits/<domain>.md
(findings emitted via
 `agentrc worker result`;
 orchestrator stages +
 commits on branch
 orc/audit-reports)
```

Key invariants:

- Phase 1 workers are **readers**. They do not modify source. They emit
  their findings doc via `agentrc worker result`; the orchestrator commits.
- The triage step is a **HARD user-approval gate**, consistent with the
  existing agentrc planning protocol.
- Phase 2 workers are **writers** on isolated worktrees. Every bucket
  branch passes through the skill's REVIEW GATE before merge.
- Merges land on `master` reactively as buckets complete — never waiting
  for all buckets before integrating.

## Phase 1 — Audit workers

Six task briefs at `.orchestrator/active/tasks/<task_id>-<slug>.md`. The
`task_id` is the 3-digit numeric used for `agentrc spawn`; the brief
filename carries both id and slug so readers can identify the brief on
disk.

| Task id | Brief filename | Domain | Specialist subagents | Focus |
|---|---|---|---|---|
| `001` | `001-audit-test-coverage.md` | test-coverage | `voltagent-qa-sec:qa-expert` + `voltagent-qa-sec:test-automator` | Coverage gaps, missing edge-case tests, untested error branches, integration vs unit balance, flaky patterns, test isolation |
| `002` | `002-audit-security.md` | security | `voltagent-qa-sec:security-auditor` + `voltagent-qa-sec:code-reviewer` | Unsafe code, path traversal, tmux/shell injection vectors, git-command handling, file locking races, `.orchestrator/` trust boundary |
| `003` | `003-audit-performance.md` | performance | `voltagent-qa-sec:performance-engineer` | Hot paths (status aggregation, event tailing, dashboard render), allocation patterns, fs walks, unnecessary clones, render rate limiting |
| `004` | `004-audit-code-quality.md` | code-quality | `voltagent-qa-sec:code-reviewer` + `voltagent-dev-exp:refactoring-specialist` | Module boundaries, duplication, over-long files, error-handling consistency, clippy findings, naming |
| `005` | `005-audit-product-spec.md` | product-spec | `voltagent-biz:product-manager` + `voltagent-biz:technical-writer` | README / SKILL.md / CLAUDE.md alignment with code, gaps between documented behavior and actual CLI, missing user-facing docs, command surface coherence |
| `006` | `006-audit-rust-impl.md` | rust-impl | `voltagent-lang:rust-engineer` + `voltagent-qa-sec:architect-reviewer` | Idiomaticity, trait/lifetime use, `unsafe`, error type hierarchy, `Cargo.toml` hygiene, dep choices, feature flags, `lib.rs` surface |

Before spawning phase 1, the orchestrator verifies that the
non-voltagent-lang/qa-sec subagent namespaces referenced above
(`voltagent-biz:*`, `voltagent-dev-exp:*`) are available in the
environment. If any are missing, the closest available specialist is
substituted and the substitution is noted in the phase-1 plan before
user approval.

Shared brief contract:

- **Role:** reader. No source file modifications. Output via `agentrc
  worker result`.
- **Scope:** full `src/` and `tests/` trees. Exclude `target/`.
  Product-spec and rust-impl auditors additionally read `docs/`,
  `README.md`, `CLAUDE.md`, and `skill/agentrc/`.
- **Output path:** `docs/audits/<domain>.md`.
- **Model:** subagent dispatches pinned to `model: "opus"`.
- **Concurrency:** all six spawn simultaneously; no inter-dependencies.
  `.orchestrator/config.json` `max_workers` must be ≥ 6 before phase 1
  begins (the orchestrator bumps it temporarily if needed and restores
  the prior value at run archive). Readers share the main worktree;
  this is the agentrc-supported pattern — they do not conflict because
  none writes to source.
- **Output directory creation:** `docs/audits/` is a new directory.
  The orchestrator creates it as part of staging the first audit
  result on `orc/audit-reports`; auditors themselves never touch the
  filesystem outside their `agentrc worker result` output.
- **Subagent git rule:** every Agent dispatch prompt includes "Do NOT run
  any git commands. Write/edit files only. I will handle all git
  operations."

Finding schema (every entry in every audit doc follows this structure):

```markdown
## F-<NN>: <title>
- **Severity:** critical | high | medium | low
- **Location:** `path/to/file.rs:LINE` (or range)
- **Description:** what's wrong, one paragraph.
- **Proposed remediation:** concrete change.
- **Confidence:** high | medium | low
```

Report front matter for each audit doc:

- Domain name
- Totals by severity
- One-paragraph summary
- Full finding list

## Triage gate

Executed by the orchestrator (not a worker) after all six phase-1 audit
docs are reviewed and merged.

1. **Read** all six `docs/audits/<domain>.md`.
2. **Normalize and de-dup:** when two domains flag the same file+issue,
   merge into one finding keeping the stronger severity and both domain
   tags.
3. **Bucket into fix tasks** by (domain, severity). Empty buckets are
   skipped. A single `deferred-low` bucket collects every low-severity
   finding across all domains; this bucket is never dispatched — it is
   written to `docs/audits/backlog.md` as the deferred record.

   Buckets are created dynamically from the findings; the table below
   is illustrative, not canonical — a bucket exists if and only if
   triage assigns at least one finding to it.

   | Bucket id | Contents |
   |---|---|
   | `security-critical` | security severity=critical |
   | `security-high` | security severity=high |
   | `perf-critical`, `perf-high` | performance |
   | `test-coverage-high`, `test-coverage-medium` | test gaps |
   | `code-quality-high`, `code-quality-medium` | quality debt |
   | `rust-impl-high`, `rust-impl-medium` | idiomaticity/architecture |
   | `product-spec-high` | doc / product drift |
   | `deferred-low` | all severity=low across domains (backlog only) |

   The `deferred-low` bucket is written to `docs/audits/backlog.md`
   during this triage step (not at run completion) and is included in
   the same commit that lands the approved fix plan, so the deferred
   record is durable even if phase 2 is later abandoned.

4. **Order buckets** by priority: security → perf → rust-impl →
   code-quality → test-coverage → product-spec. Higher-priority buckets
   merge first so later buckets rebase onto the latest state and
   invalidated findings can be dropped.
5. **Write the fix plan** to `.orchestrator/active/plan.md` — DAG with one
   task per bucket, dependencies encoding the ordering above, expected
   files touched, review requirements.
6. **HARD GATE:** user approves the plan before any phase-2 spawn. User
   may remove buckets, demote findings to backlog, or re-scope.

## Phase 2 — Fix workers

One agentrc writer task per approved bucket. Task id is a 3-digit
numeric starting at `101` (`101`, `102`, …); brief filename is
`<task_id>-fix-<bucket>.md`; branch is
`orc/<task_id>-fix-<bucket>`. Example: bucket `security-critical`
becomes task id `101`, brief
`.orchestrator/active/tasks/101-fix-security-critical.md`, branch
`orc/101-fix-security-critical`.

Brief contract:

- **Role:** writer. Own worktree, own branch, `agentrc worker *` for
  status.
- **Findings list:** copied verbatim from the triage doc — every finding
  in this bucket with its proposed remediation and confidence.
- **Specialist dispatch:** same domain specialists used by the
  corresponding auditor (see Phase 1 table), with `model: "opus"`.
- **TDD contract:** every fix lands with a test. When the finding itself
  is a missing-test finding, the new test is the deliverable. For
  implementation fixes, write a failing test first that demonstrates the
  defect, then fix it.
- **Atomic edits:** all edits then `cargo fmt && cargo build && cargo
  test` green, then a single commit per logical unit. Never commit
  between edits. Never commit a broken build.
- **Completion criteria:** every finding in the bucket is either (a)
  fixed with a test, or (b) documented as deferred-with-reason in the
  worker's `agentrc worker result` note — orchestrator acks before
  teardown.

Concurrency:

- Buckets from **different domains** run in parallel.
- Buckets within the **same domain** (e.g., `security-critical` →
  `security-high`) run sequentially; the higher-severity bucket must
  integrate first. This prevents the lower-severity bucket from rebasing
  on a moving target.
- Cross-domain file collisions identified during triage are encoded as
  DAG dependencies.
- Standard agentrc priority saturates `max_workers` with the
  highest-priority bucket first.

Redispatch policy: max 2 redispatches per bucket, then pause and surface.
No auto-redispatch without user confirmation.

## Review and integration

Phase 1 audit-doc integration:

- Orchestrator stages and commits all six docs on `orc/audit-reports` in
  the main worktree (readers do not commit).
- Pre-merge review panel: `voltagent-biz:technical-writer` (report
  quality) + `voltagent-qa-sec:code-reviewer` (accuracy of file:line
  citations, hallucination check).
- Address blockers, then `git merge --no-ff`. Triage begins once merged.

Phase 2 bucket integration:

- Full REVIEW GATE: `voltagent-lang:rust-engineer` +
  `voltagent-qa-sec:security-auditor` on every diff. Up to two additional
  domain specialists may be added where relevant (e.g.,
  `voltagent-qa-sec:performance-engineer` for perf buckets).
- On pass: `git merge --no-ff orc/<branch>` followed by a post-merge
  `cargo fmt && cargo build && cargo test`. Direct merge is preferred
  over `agentrc integrate` for per-bucket control — `integrate`
  operates on all ready writer tasks in the active run and does not
  scope to a single bucket.
- Integrate reactively — do not wait for all buckets.
- Test failure or unresolved review blocker → fix in-place on the bucket
  branch, or redispatch with user approval.

Failure handling:

- Audit worker crash → respawn from existing state (findings doc is
  additive; worker resumes from its own notes).
- Fix worker cannot reproduce a finding → documented in a per-run
  `deferred-findings.md` addendum, surfaced at completion.
- Review blocker with no clear fix → escalate to user; never silently
  merge.

Completion criteria for the full run:

1. `orc/audit-reports` merged to `master` (six audit docs present).
2. Every non-deferred bucket merged to `master` with tests green.
3. `docs/audits/backlog.md` written with deferred low-severity findings.
4. `docs/audits/deferred-findings.md` written if any fix worker was
   unable to reproduce or address a finding assigned to its bucket;
   absent otherwise.
5. If triage produces zero non-deferred buckets (no high/critical
   findings survive the gate), the run short-circuits: the
   `deferred-low` bucket is still written to `docs/audits/backlog.md`,
   phase 2 is skipped, and the run archives with a "no remediation
   required" note.
6. `agentrc run archive`.
7. Final summary report: what was found, what was fixed, what was
   deferred, full merge history.

## Tooling surface

agentrc commands exercised by this run:

- `agentrc run create --slug comprehensive-audit`
- `agentrc spawn 001` through `agentrc spawn 006` (phase 1; six
  invocations, one per numeric task id — `spawn` takes the numeric id
  only and locates the brief by `<task_id>-*.md` prefix match)
- `agentrc status` and `agentrc dashboard` for monitoring
- `agentrc teardown <task_id>` per auditor (numeric id), executed
  only after the consolidated `orc/audit-reports` branch has merged —
  not per individual doc
- `agentrc spawn 101`, `agentrc spawn 102`, … per approved bucket
  (phase 2)
- Per-bucket merges: `git merge --no-ff orc/<task_id>-fix-<bucket>`
  with post-merge `cargo build && cargo test`. `agentrc integrate` is
  not used per-bucket because it merges all ready writers together;
  it is an option for a final sweep if many buckets are left at once.
- `agentrc checkpoint save` at phase transitions
- `agentrc run archive` at completion

No git operations performed by workers or subagents. Orchestrator is the
sole git authority for branching, merging, and remote operations.

## Out of scope

- CI / release automation changes.
- Dependency upgrades (may appear as rust-impl findings but are deferred
  to a separate spec unless triage elevates them).
- Refactors beyond what is needed to address a specific finding.
- Adding new features. This is strictly an audit-and-fix sweep.
