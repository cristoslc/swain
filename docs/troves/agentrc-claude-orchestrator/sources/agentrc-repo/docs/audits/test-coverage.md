---
domain: test-coverage
task_id: "001"
auditors:
  - voltagent-qa-sec:qa-expert
  - voltagent-qa-sec:test-automator
scope: src/ and tests/ (excluding target/)
generated_at: 2026-04-12
totals:
  total: 117
  critical: 10
  high: 27
  medium: 41
  low: 39
numbering_note: Findings use F-NNN (3-digit) because count exceeds 99; other audit docs use F-NN. Severity and confidence values follow the canonical schema.
---

# Audit 001 — Test Coverage & Quality (phase 1 reader)

## Summary

118 findings (10 critical, 27 high, 41 medium, 40 low) after consolidating 6 cross-specialist duplicates from the 124 raw findings returned. Coverage is broad at the CLI boundary via `assert_cmd` smoke tests and mid-level via per-command integration tests, but critical orchestration entry points (`spawn::run`, `respawn::run_in`, `checkpoint::restore_in`, `tui::action::handle_key`) have **no direct coverage**. Recurring themes: (1) untested panics and `?`-swallowed errors along mutation paths; (2) file-based event bus (statuses, notes, events) is not atomic and has zero concurrency tests; (3) `tests/common/mod.rs` is under-developed — `init_test_repo` inherits developer-global git config (`init.defaultBranch`), `serial_test` is absent despite env-var-sensitive tests, and ~15 files duplicate brief-building boilerplate; (4) weak assertions (`is_err()` without variant check, short substring matches that accept too much, existence-only checks missing content assertions); (5) `AppError` has 11 variants with no display assertion and 4+ that appear dead; (6) exhaustive enum round-trips for `EventType`, `Severity`, `TaskState`, `DetectedState` are missing, making schema renames silent breakages.

Severity was scaled against the blast radius on an orchestration run: critical = a regression breaks spawn/integrate/recovery for every user; high = data-loss or merge-corruption exposure on a real code path; medium = observable-but-contained defect; low = cosmetic, dead-code, or latent-only.

---

## F-001: `serial_test` is not a dev-dependency yet multiple tests touch process-global state
- **Severity:** critical
- **Location:** `Cargo.toml:25-29`
- **Description:** `cargo test` runs tests in parallel by default, including tests from different `tests/*.rs` files within the same binary. Several tests inspect or depend on process-global state that is not safely parallelisable: `Tmux::is_inside_tmux()` at `tests/tmux_test.rs:33` reads the `TMUX` env var; `git` inherits the developer's global `$HOME`, GPG agent, and `user.signingkey`; the process cwd is read by every child `git` invocation. `Cargo.toml` does not declare `serial_test` as a dev-dependency, so there is no primitive available to protect against parallel data races. If any future test adds `env::set_var` or `env::set_current_dir` (the audit-sweep plan explicitly anticipates this), there is no guard.
- **Proposed remediation:** Add `serial_test = "3"` to `[dev-dependencies]`. Annotate `tmux_is_inside_checks_env` with `#[serial]`. Establish a convention (in `tests/common/mod.rs` doc-comment) that any test touching env vars, cwd, `$HOME`, or a real tmux server must carry `#[serial]`. Add a CI lint that greps for `env::set_var`, `env::set_current_dir`, and `std::process::Command::new("tmux")` in `tests/` and fails if the surrounding fn lacks `#[serial]`.
- **Confidence:** high

## F-002: `commands::checkpoint::restore_in` (lossy-recovery walk) has zero direct coverage
- **Severity:** critical
- **Location:** `src/commands/checkpoint.rs:198-275`
- **Description:** `tests/checkpoint_test.rs` tests only `save_in` (twice). The entire restore flow — latest-checkpoint selection (`entries.last()`), explicit id lookup (`active.checkpoint_file(id)` with missing file), `branch_exists`/`log_branch_commits` decoding, the "LOST (branch missing)" and "empty (no commits)" branches at `checkpoint.rs:243-256`, and the `respawn=true` cascade at `checkpoint.rs:264-272` — has zero coverage. An id passed to `restore_in` that does not exist yields a `std::fs::read_to_string` error at `checkpoint.rs:220`; that error message path is also untested. If `restore_in` silently misreports `LOST` vs `ok`, operators won't know their run is unrecoverable until they try.
- **Proposed remediation:** Add `restore_in` tests covering: (a) no checkpoints at all → error, (b) explicit id referencing a missing file → error, (c) checkpoint referencing a deleted branch → recovery column reports "LOST", (d) checkpoint referencing a branch with no commits → reports "empty", (e) `respawn=true` with eligible in-progress task → invokes respawn. Because live respawn needs tmux, inject a `RespawnFn` trait or move the respawn loop behind a boolean result so it can be asserted without actually respawning.
- **Confidence:** high

## F-003: `dry_run_in` panics when a writer brief is missing `branch`
- **Severity:** critical
- **Location:** `src/commands/integrate.rs:194-198`
- **Description:** `dry_run_in` unwraps `task.branch` with a raw `panic!("writer task {} has no branch", task.id)`. `TaskBriefFrontmatter::branch` is optional in the frontmatter schema, so a brief classified as `writer` without an explicit `branch:` line will abort the whole process instead of returning an error. No test constructs a writer brief with `branch: null` or a missing `branch` field to exercise this path; `setup_two_writer_tasks` and friends always set the branch. A malformed brief in production would kill the CLI with a panic instead of surfacing a proper `AppError`.
- **Proposed remediation:** Replace the `panic!` with an `anyhow::bail!` (or a dedicated `AppError::MissingBranch`) so the error propagates, and add a test that writes a writer brief with no `branch:` field and asserts `dry_run_in` returns `Err` rather than crashing. Mirror the same change at `integrate.rs:275-278` (see F-004).
- **Confidence:** high

## F-004: `integrate_in` panics on missing `branch` in writer brief
- **Severity:** critical
- **Location:** `src/commands/integrate.rs:275-278`
- **Description:** The second loop over `tasks` inside `integrate_in` also unwraps `task.branch` with `panic!("writer task {} has no branch", ...)`. This is reachable any time a writer brief omits the `branch` field (the type models it as `Option<String>`). The happy-path tests always provide a `branch`, so the panic branch is untested. Because `integrate_in` is invoked from the CLI `run()`, a single malformed brief turns into a crash rather than a `MergeResult { success: false, ... }` entry.
- **Proposed remediation:** Replace the `panic!` with a pushed `MergeResult` marking the task failed (or bail from the function), and add a regression test that mixes one well-formed writer brief with one that is missing `branch`.
- **Confidence:** high

## F-005: `commands::respawn::run_in` (kill + rebuild worker pane) has zero direct coverage
- **Severity:** critical
- **Location:** `src/commands/respawn.rs:20-137`
- **Description:** Only the pure helpers `validate_respawn` and `generate_resume_seed` are tested (`tests/respawn_test.rs`). The full `run_in` body — which kills the old pane, removes and recreates the worktree from the existing branch, increments `redispatch_count`, writes back the status file, rewrites the brief with the new `pane_id`, and emits a `Respawned` event — is never invoked in tests. Any mutation bug in the status-write, brief-frontmatter update, or redispatch increment path will go undetected. The `max_redispatch_attempts` guard (line 41-47) is also uncovered.
- **Proposed remediation:** Mirror `spawn`'s proposed mock-tmux seam (F-006) and add a `respawn_run_in_increments_redispatch_and_updates_status` test that drives `run_in` end-to-end against a tempdir, then asserts on status.redispatch_count, status.pane_id (via stubbed tmux), brief frontmatter, and the event log.
- **Confidence:** high

## F-006: `commands::spawn::run` (top-level spawn orchestration) has zero direct coverage
- **Severity:** critical
- **Location:** `src/commands/spawn.rs:103-242`
- **Description:** The public `run(task_id)` entry point is the only function in `spawn` that chains task-brief lookup, config parsing, max-worker enforcement, worktree setup, tmux window/pane provisioning, frontmatter pane_id upsert, status-file pane_id/pane_title patch, layout retile, env export, cd/heartbeat/claude launch, and event emission. Tests cover the individual helpers (`setup_worktree`, `write_initial_status`, `find_task_brief`, `load_task_brief`, `generate_seed_prompt`) but nothing exercises the full orchestration — including the max_workers bail branch (line 133-139), the pane_id-to-status patch (line 183-191), the writer-vs-reader cwd selection (line 203-208), and the claude command string assembly with `worker_claude_args` (line 227-231). A regression here will silently break every spawn.
- **Proposed remediation:** Add a mockable tmux boundary (inject a trait or feature-gate the tmux calls) and write a `spawn_run_full_flow` test that verifies: brief frontmatter gets `pane_id` upserted, status JSON has both `pane_id` and `pane_title`, `max_workers` limit returns error when exceeded, and reader tasks skip worktree creation. Even a partial test that stops at the first `Tmux::new()` call would catch the pre-tmux logic.
- **Confidence:** high

## F-007: Status-mutating CLI error paths leave many `AppError` variants unasserted
- **Severity:** critical
- **Location:** `src/model/error.rs:31-49` (and `1-56`)
- **Description:** Eight-plus `AppError` variants are never asserted against in any test: `WorktreeExists` (spawn.rs:71), `BranchExists` (defined but never constructed — dead variant?), `DirtyBaseBranch` (defined but never constructed), `TmuxError`/`GitError` (defined but never constructed — all tmux/git failures propagate as anyhow strings instead), `TaskBriefParseError` (spawn.rs:25), `StatusParseError` (status.rs:80, teardown.rs:94, worker/status.rs:49), `InvalidStateTransition` (defined but `can_transition_to` is tested only in isolation — the error variant itself is never returned by the codebase), `TestFailure` (defined but integrate.rs returns the failure inside `MergeResult` instead), `RunAlreadyActive`, `TaskNotFound`, `AmendSourceRequired`. `tests/model_test.rs` asserts on only six variants total. Many of these are either dead code or live branches whose error messages will only be seen in production.
- **Proposed remediation:** Two parts. (1) Add negative tests for each live variant: `spawn_worktree_exists_returns_worktree_exists_error`, `worker_status_parse_error_on_malformed_json`, `teardown_status_parse_error_on_malformed_json`, `spawn_load_brief_parse_error_on_bad_yaml`, plus one parameterized `app_error_display_exhaustive` test that walks every variant via a `vec![(err, expected_prefix), …]` table. (2) Decide whether `BranchExists`, `DirtyBaseBranch`, `TmuxError`, `GitError`, `InvalidStateTransition`, `TestFailure` are dead code — if so, delete them; if intended for future use, add `#[allow(dead_code)]` with a TODO and a tracking issue.
- **Confidence:** high

## F-008: Key-event dispatch table (`action::handle_key`) has zero unit tests
- **Severity:** critical
- **Location:** `src/tui/action.rs:18-85`
- **Description:** `action::handle_key` is the entire keyboard command surface of the TUI — it routes `z`, `t`, `r`, `a`, `i`, `c` keys into `Action::Shell(...)` commands that shell out to `tmux` / `agentrc` subcommands with the selected task id. There are no tests anywhere (neither inline `#[cfg(test)]` nor in `tests/`) exercising this function. All of the non-trivial gating logic — dead-task guard (lines 24, 29-31, 45-47, 69-71), `pane_id` presence guard for `z` (lines 32-41), the narrower `Failed | Aborted` match for `r` (line 57), and the global `i`/`c` actions (lines 81-82) — is therefore unverified. Regressions that e.g. allowed respawning `Completed` tasks or tearing down graveyard tasks would silently ship. The function is trivially unit-testable because `App` can already be constructed in-memory (see `src/tui/app.rs:260` `test_app` helper).
- **Proposed remediation:** Add unit tests (either in `src/tui/action.rs` inline or in `tests/action_test.rs`) covering at least one case per branch: (a) each alive-only key returns `Action::Shell` with the correct argv for an alive task; (b) each alive-only key returns `Action::None` for each graveyard state (`Completed`, `Failed`, `Aborted`); (c) `z` returns `None` when `pane_id` is `None`; (d) `r` returns `None` for `Completed` but `Shell` for `Failed`/`Aborted`; (e) `i` and `c` always return `Shell`; (f) unknown keys (e.g. `'x'`) return `None`; (g) empty status list (`selected_status() == None`) returns `None`. Reuse the existing `test_app` helper pattern.
- **Confidence:** high

## F-009: `init_test_repo` silently depends on the developer's global git `init.defaultBranch`
- **Severity:** critical
- **Location:** `tests/common/mod.rs:16-24`
- **Description:** `init_test_repo` shells out to `git init <path>` with no `--initial-branch` flag and no `GIT_CONFIG_GLOBAL=/dev/null` isolation. The resulting branch is whatever the invoking developer's global git config says (`init.defaultBranch`), or falls back to `master` on older gits and `main` on newer ones. Downstream tests then assume very specific branch names: `tests/audit_test.rs:85,184,295` and `tests/respawn_test.rs:32,71` and `tests/checkpoint_test.rs:27` hardcode `master` in task briefs or `git checkout master`, while `tests/fs_test.rs:131,163,182` and `tests/plan_test.rs:29` hardcode `main`. Anyone who sets `init.defaultBranch=main` globally (the GitHub default since 2020) will break every `audit_test` and `respawn_test`; anyone on legacy `master` default will break the fs_test/plan_test. This is environmental contamination — the same commit passes on one machine and fails on another.
- **Proposed remediation:** In `tests/common/mod.rs`, pass `--initial-branch=master` (or `main` — pick one) to `git init`, or call `git -c init.defaultBranch=master init`. Also set a sentinel `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_SYSTEM` to `/dev/null` inside `run_git_checked` so developer-global hooks, templates, and signing config cannot leak in. Then update every test that hardcodes a branch name to use `Git::new(path).current_branch()` instead of a string literal.
- **Confidence:** high

## F-010: `respawn_test` swallows subprocess exit codes — tests pass even when `git commit` silently fails
- **Severity:** critical
- **Location:** `tests/respawn_test.rs:22-29`
- **Description:** The helper `setup_in_progress_task` runs `git add work.txt` and `git commit -m "work in progress"` with `let _ = Command::new("git").args(…).current_dir(&wt_path).output();`. The return value is discarded — no check of `output.status.success()`, no check of stderr. If git config is broken (no `user.email`, no `user.name`, the `init_test_repo` helper's per-repo config missed a worktree, or the worktree is somehow not recognised), the commit silently fails and `respawn_generates_resume_seed` and `respawn_rejects_missing_branch` still "pass" because the test downstream only re-reads the status file. Combined with F-009, this is a silent correctness hole.
- **Proposed remediation:** Replace the two `let _ = …output();` calls with `common::init_test_repo`-style `run_git_checked` helpers that assert `status.success()` and panic with stderr on failure. Or use the existing `agentrc::git::wrapper::Git::new(&wt_path).add_all()` / `.commit()` paths (which `git_test.rs` already exercises) — they return `Result` and are tested.
- **Confidence:** high

## F-011: TDD-violation event emission (`audit::audit_tdd` warn path) unasserted
- **Severity:** high
- **Location:** `src/audit.rs:77-80`
- **Description:** When a branch has no test commits, `audit_tdd` emits a `TddViolation` warn event. `tests/audit_test.rs::audit_no_tests` verifies `result.compliant == false` but does not read `events.jsonl` to confirm the event fired. A regression where the event is dropped — or swaps `Severity::Warn` for `Severity::Info`, or `continue`s past line 79 — will leave dashboards/watchers silently degraded with no test signal.
- **Proposed remediation:** Extend `audit_no_tests` (or add `audit_no_tests_emits_tdd_violation_event`) to assert that after `audit_tdd`, `events::tail(root, 10)` contains exactly one event with `event_type == EventType::TddViolation`, `severity == Severity::Warn`, `task_id == Some("001")`, and a message containing `"TDD violation"`.
- **Confidence:** high

## F-012: `commands::checkpoint::list_in` not directly tested
- **Severity:** high
- **Location:** `src/commands/checkpoint.rs:158-190`
- **Description:** Prints table; no test verifies sort order, empty-dir message, or checkpoint parse behaviour. Two early-return paths — the checkpoints dir missing (line 163) and the directory empty (line 174) — are both untested. A change that flipped the sort order or skipped the JSON extension filter would silently corrupt output, and the "has entries" formatting path is never asserted.
- **Proposed remediation:** Make `list_in` return a `Vec<CheckpointSummary>` (mirroring how `commands::run::list_in` returns `Vec<RunInfo>`) and separate the formatting from the CLI. Then add three tests: `list_in_empty_returns_no_panic_and_empty_message`, `list_in_non_json_files_reported_as_empty`, `list_in_sorts_by_id` (save two checkpoints, assert id order).
- **Confidence:** high

## F-013: `integrate_in` checkout-failure path is untested and poorly diagnosed
- **Severity:** high
- **Location:** `src/commands/integrate.rs:268-269`
- **Description:** `git.checkout(&config.base_branch)` is called unconditionally. If the base branch does not exist, has been deleted, or the working tree is dirty, `checkout` returns an error and `integrate_in` bails with a generic context string. No test exercises a dirty working tree at the time of integration, a missing base branch, or a detached HEAD. The CLI fails loudly with a `with_context` message but no structured diagnostic — the user gets no hint about uncommitted files.
- **Proposed remediation:** Before checkout, call `git.is_clean()` and `git.branch_exists(&config.base_branch)` to produce an `AppError::DirtyWorktree` / `AppError::BaseBranchMissing`. Add tests that write an uncommitted file to the base repo and assert a clear error, plus a test where the base branch is deleted.
- **Confidence:** high

## F-014: Merge-result event emissions (MergeStarted / MergeSuccess / MergeConflict / MergeTestFail) have no assertions
- **Severity:** high
- **Location:** `src/commands/integrate.rs:286-291, 334-340, 357-362, 405-411`
- **Description:** `integrate_in` calls `events::emit_info`/`emit_warn` for each merge lifecycle transition, but no test in `tests/integrate_test.rs` reads the `events.jsonl` file after an integrate run to verify the event stream. A silent failure to emit (e.g. `.unwrap_or(())` swallowing a broken log path) will not break any test. This is the observability contract for the orchestrator.
- **Proposed remediation:** Append to the existing `integrate_merges_independent_tasks` / `integrate_detects_merge_conflict` tests an assertion that `events::tail(project_root, 10)` contains the expected `MergeStarted`/`MergeSuccess`/`MergeConflict`/`MergeTestFail` events in order. Use the same pattern for `CheckpointSaved` in `tests/checkpoint_test.rs` and `Spawned`/`Respawned` in new F-005/F-006 tests.
- **Confidence:** high

## F-015: Integration test-failure reset-and-rollback semantics not separately asserted
- **Severity:** high
- **Location:** `src/commands/integrate.rs:295-341`
- **Description:** `tests/integrate_test.rs::test_failure_diagnostics_includes_stderr` asserts `test_failure == true` and stderr capture, but does NOT assert that `git.reset_hard_head(1)` successfully removed the merge commit from the base branch. A regression that keeps the broken merge on main (the worst possible bug for integration) is undetected. The test checks stderr content but not git state post-rollback.
- **Proposed remediation:** After the `integrate_in` call in `test_failure_diagnostics_includes_stderr`, assert that `!tmp.path().join("feature.txt").exists()` (the file from the reverted merge should be gone) and that `git.log_oneline(base_branch, 10)` no longer contains the merge commit subject.
- **Confidence:** high

## F-016: `integrate_in` test-failure reset assumes exactly 1 merge commit
- **Severity:** high
- **Location:** `src/commands/integrate.rs:319-320`
- **Description:** `git.reset_hard_head(1)` unconditionally rolls back one commit on test failure. If `merge_no_ff` happened to fast-forward (it shouldn't with `--no-ff`, but if the config ever changed) or if pre-merge hooks added an extra commit, this blindly drops the wrong commit. More importantly, if `reset_hard_head(1)` itself fails (repo state, hook), the error is `let _`-swallowed and the next iteration's `git.merge_no_ff` will fail mysteriously. No test asserts what happens when reset fails.
- **Proposed remediation:** Capture `HEAD` via `rev_parse` before the merge and `reset --hard <pre_merge_sha>` after a test failure instead of `HEAD~1`. Propagate reset errors with clear diagnostics. Add a test that hooks reset to fail (e.g. by making the worktree read-only) and asserts the bail.
- **Confidence:** high

## F-017: Test-command subprocess failure modes are under-tested
- **Severity:** high
- **Location:** `src/commands/integrate.rs:485-506`
- **Description:** `run_tests_with_output` shells out via `sh -c`. Only a single happy-ish path is tested (`test_failure_diagnostics_includes_stderr`, where the command exits 1 and writes to stderr). Uncovered: (a) `Command::new("sh").output()` returns `Err` (e.g. missing `sh`) — hits line 501 but no test forces it; (b) command succeeds but writes nothing to stderr while still exiting 0 — no test confirms `stderr` is `None`; (c) very long stderr exceeding the 50-line truncation at line 305 — no test verifies `truncate_lines` actually bounds the output; (d) a test command that hangs indefinitely (no timeout) — blocks the integrate flow forever.
- **Proposed remediation:** Add tests: (1) set `test_command` to a 200-line stderr emitter and assert `test_stderr` is exactly 50 lines, (2) set `test_command` to a command that only writes to stdout and exits 0 → `test_stderr` is `None`, (3) point the command at a non-existent binary → bail with helpful message. Also consider adding a per-invocation timeout (e.g. wrap with `timeout` or spawn + wait_timeout) and test it.
- **Confidence:** high

## F-018: `plan::validate_briefs` tested only via `validate_in`; pure-function surface untested
- **Severity:** high
- **Location:** `src/commands/plan.rs:76-136`
- **Description:** `validate_briefs(&[TaskBriefFrontmatter])` is `pub` and pure, but `tests/plan_test.rs` always goes through `validate_in` (which requires a tempdir + git repo + brief files on disk). That adds ~100ms per case and makes edge-case enumeration painful. The cycle detection branch (`detect_cycle`) is tested once for a 3-cycle; the 2-cycle, 4-cycle, and self-loop diagnostic message formats are not independently asserted.
- **Proposed remediation:** Add direct `validate_briefs` unit tests that build `TaskBriefFrontmatter` in-memory and check the error message formatting (e.g. "A → B → A"). This also serves as coverage for `detect_cycle`'s path-trace logic on line 211-232.
- **Confidence:** medium

## F-019: `plan::topo_sort` public API has no direct unit test
- **Severity:** high
- **Location:** `src/commands/plan.rs:239-275`
- **Description:** `topo_sort` is `pub` and is shared between `plan validate` and `integrate`. Its merge ordering is asserted only transitively via `tests/happy_path.rs::e2e_dependent_tasks_merge_in_order` and via the integrate tests that happen to produce consistent order. There is no direct test for: (a) stable id-tiebreak ordering among same-depth tasks, (b) the "cycle / unresolvable — append rest" fallback branch (line 260-264), (c) behaviour when `depends_on` references an unknown id (`!ids.contains(dep)` path on line 254). A regression that changes merge order in a subtle way will break real integrations without any unit-level signal.
- **Proposed remediation:** Add `tests/plan_test.rs` cases: `topo_sort_ties_break_by_id`, `topo_sort_preserves_diamond_order`, `topo_sort_with_unknown_dep_ignores_it`, `topo_sort_with_cycle_appends_remaining_in_id_order`.
- **Confidence:** high

## F-020: `respawn::run_in` max-redispatch bail is not covered
- **Severity:** high
- **Location:** `src/commands/respawn.rs:40-47`
- **Description:** `respawn::run_in` bails when `status.redispatch_count >= config.max_redispatch_attempts`. The existing tests (`respawn_test.rs`) only cover `validate_respawn`, so this branch is never hit. Additionally, `validate_respawn` does NOT check `redispatch_count`, so a test that exercises the cap must go through `run_in` (which also requires a live tmux server, currently impossible to test). There is no testable seam for this limit.
- **Proposed remediation:** Extract the redispatch-count check into a pure helper (e.g. `check_redispatch_limit(status, config)`) called before any tmux/git mutation, and add a unit test that seeds `redispatch_count = max` and asserts the helper errors. Alternatively, move the check into `validate_respawn` so the existing testable entry point enforces it.
- **Confidence:** high

## F-021: Config `max_workers` gate in `spawn::run` has no test
- **Severity:** high
- **Location:** `src/commands/spawn.rs:119-139`
- **Description:** Spawn loads `max_workers` from config and rejects spawns when the count of `Spawning|Ready|InProgress|Blocked` tasks reaches the limit. This logic is entirely untested — `tests/spawn_test.rs` only exercises `load_task_brief`, `setup_worktree`, `write_initial_status`, and `generate_seed_prompt`, never calling `spawn::run`. A regression that mis-counts `Blocked` tasks (or flips the comparison to `>`) would ship unnoticed.
- **Proposed remediation:** Factor the cap check into a small helper (e.g. `fn check_worker_budget(project_root, config) -> Result<()>`) and write a test that seeds N statuses at various states and asserts the bail fires with the expected message (`"max workers (...) reached"`).
- **Confidence:** high

## F-022: `worker::done::run_in` permits double-done and done-without-in-progress
- **Severity:** high
- **Location:** `src/commands/worker/done.rs:24-62`
- **Description:** Calling `done` twice simply sets `state = Completed` twice and re-rings the bell — nothing prevents it. Similarly, calling `done` on a task whose status was never written succeeds (status file is created by `worker::status::run_in` on the fly). Neither edge case has a test. The `result_path` is overwritten if `done` is called twice with different result files, losing the first one. This directly matches the audit item "done after done" and "heartbeat after done".
- **Proposed remediation:** Read the existing status (if present) and bail when `state == Completed` or `Aborted`, unless `--force`. Tests: (1) call `done` twice → second returns error; (2) `done` on a task with no prior status → error (or auto-create with message).
- **Confidence:** high

## F-023: `worker::status::run_in` accepts illegal state transitions
- **Severity:** high
- **Location:** `src/commands/worker/status.rs:30-108`
- **Description:** The state machine is a free-for-all: a task can go `completed → in_progress → completed` or `aborted → spawning` without error. The only validation is `parse_state`, which rejects bad strings. No test asserts illegal transitions are blocked, because they are NOT blocked. A worker that crashes after marking itself done can silently re-open its own task by writing a new status file. Additionally, `phase_history.push` always appends, so repeated writes balloon the file unboundedly — no test caps history size.
- **Proposed remediation:** Introduce `fn is_valid_transition(from: TaskState, to: TaskState) -> bool` implementing the allowed DAG (Spawning→Ready→InProgress→{Completed, Failed, Blocked, Aborted}, etc.) and reject others. Add tests for each forbidden transition. Optionally cap `phase_history` length.
- **Confidence:** high

## F-024: `tail()` skips unparseable lines silently with no test coverage
- **Severity:** high
- **Location:** `src/events.rs:74-78`
- **Description:** `events::tail` intentionally drops malformed JSON lines via `filter_map(|line| serde_json::from_str(line).ok())` to survive truncated writes from crashes (comment on line 73). This is correct behavior, but no test in `tests/events_test.rs` exercises it. If a future refactor swapped `ok()` for `unwrap()` or changed the serialization, truncated-log tolerance would regress silently. Additionally, `tail` when `count > events.len()` is untested, and `tail(0)` is untested. The `emit_warn` path (lines 45-59) is also untested; all three existing tests call `emit_info`. `tail_handles_missing_log_file` returning empty `Vec` (lines 66-68) is uncovered.
- **Proposed remediation:** Add tests: (a) `tail_skips_malformed_lines` — write a mix of valid JSON and a half-written line (`{"timestamp":`), assert `tail` returns only the valid events; (b) `tail_returns_all_when_count_exceeds_available` — emit 3, call `tail(10)`, expect 3; (c) `tail_zero_returns_empty`; (d) `emit_warn_writes_severity_warn` — verify the resulting JSONL has `"severity":"warn"`; (e) `tail_handles_missing_log_file` returns empty `Vec`.
- **Confidence:** high

## F-025: `frontmatter::upsert_field`, `get_field`, `yaml_safe_value` lack dedicated tests
- **Severity:** high
- **Location:** `src/fs/frontmatter.rs:84-164`
- **Description:** Only `parse` and `update_field` are directly tested (`tests/fs_test.rs:124-194` and `src/fs/frontmatter.rs:171-201`). `upsert_field` (used by `amend::replace_brief` to preserve system fields) is covered only transitively via `tests/amend_test.rs`; the insert-new-field branch on line 137-141 is not independently asserted. `get_field` (used by `amend::replace_brief` line 113) is untested. `yaml_safe_value` — responsible for escaping every YAML-dangerous character including `@` and `!` — has no test asserting the exact quoting behaviour. The `update_field` test case using `%14` covers one special-char branch only (`%`); the other 16 branches on lines 89-106 are untested.
- **Proposed remediation:** Add `tests/fs_test.rs` cases: `upsert_field_appends_new_key`, `upsert_field_replaces_existing_key`, `get_field_returns_some_for_existing`, `get_field_returns_none_for_missing`, `get_field_returns_err_on_missing_delimiters`, and a table-driven `yaml_safe_value_escapes_special_chars` (make it `pub(crate)` if needed).
- **Confidence:** high

## F-026: `git::wrapper::Git` — several public methods untested
- **Severity:** high
- **Location:** `src/git/wrapper.rs` (broad)
- **Description:** Directly untested methods: `rev_parse` (line 92-94 — used by checkpoint::save_in), `list_worktrees` (line 81-89), `show_files_changed` (line 154-162 — looks unused), `reset_hard_head` (line 119-123 — critical for integrate rollback — only transitive via integrate tests, and per F-015 even that coverage doesn't verify its effect), `merge_abort` (line 113-116 — used on conflict path, no dedicated test), `conflicting_files` (line 177-185 — tested only transitively via integrate conflict test), `create_worktree_from_branch` (line 67-71 — used by respawn, no direct git test), `log_branch_commits` (line 146-151), `log_commits_with_files` (line 189-226 — the parser is non-trivial and only indirectly tested through `audit_tdd`), `changed_files` (line 165-174 — only transitively tested).
- **Proposed remediation:** Extend `tests/git_test.rs` with: `git_rev_parse_returns_short_hash`, `git_reset_hard_head_removes_commit`, `git_merge_abort_restores_clean_state`, `git_conflicting_files_returns_unresolved_paths` (using a deliberate merge conflict), `git_log_commits_with_files_parses_40-char_hash_boundary` (exercises the hex-detection heuristic on line 207-210, which is fragile), `git_create_worktree_from_branch_reuses_existing_branch`. Delete `show_files_changed` and `list_worktrees` if unused.
- **Confidence:** high

## F-027: `SortOrder::cycle_sort` cycles state but no code ever sorts by it
- **Severity:** high
- **Location:** `src/tui/app.rs:161-167` (consumers: `src/tui/widgets/table.rs:230-243, 285-298`)
- **Description:** `App::cycle_sort` rotates `sort_order` through `Id → State → Elapsed → Id`, but grepping the entire codebase shows no site that reads `app.sort_order` to actually order rows. `statuses` is produced by `collect_statuses` which sorts by `id` once (`src/commands/status.rs:89`) and is never re-sorted. The `s` key therefore visibly does nothing, yet the feature is advertised in the help overlay (`src/tui/widgets/help.rs:31` — "Cycle sort order") and key hint bar (`src/tui/ui.rs:109`). No test catches this: there is no assertion that switching to `SortOrder::State` actually reorders `app.statuses`, or even that the field round-trips through `cycle_sort`.
- **Proposed remediation:** Either (a) wire `sort_order` into `render_workers` / `render_graveyard` and add a unit test: build an `App` with out-of-order ids/states/elapsed, call `cycle_sort`, assert the rendered/exposed row order changes accordingly; or (b) if the feature is intentionally dormant, add a regression test asserting `cycle_sort` cycles the enum variants in the documented order so future wiring work has a safety net.
- **Confidence:** high

## F-028: `App::handle_click` graveyard-region math is untested
- **Severity:** high
- **Location:** `src/tui/app.rs:199-249` (specifically graveyard branch 235-248)
- **Description:** Three inline tests exist for `handle_click` (`click_selects_row`, `click_with_animation_off`, `click_ignores_graveyard_rows`) but all three target only the *active* region. The graveyard-click branch (lines 235-248) computes `graveyard_box_bottom = terminal_h.saturating_sub(5)`, `graveyard_data_end = graveyard_box_bottom.saturating_sub(1)`, `graveyard_data_start = graveyard_data_end.saturating_sub(graveyard_count as u16)` — all of this fragile terminal-bottom-relative arithmetic is unverified. A click on a graveyard row should set `self.selected = active_count + gy_index`, but no test asserts that. Edge cases: very short terminals (`terminal_h < 5` triggers `saturating_sub`), zero graveyard rows but a click falling in the region (line 235 guard), and clicks exactly on `graveyard_data_end` (exclusive upper bound, line 243).
- **Proposed remediation:** Add unit tests mirroring the existing ones: (a) click on a graveyard row selects `active_count + gy_index` for a mix of 2 active + 2 graveyard statuses with `terminal_height = 40`, `show_animation = false`; (b) click just below `graveyard_data_start` and just above `graveyard_data_end` — assert boundary behavior; (c) click when `terminal_height = 0` does not panic and does not change `selected`; (d) click with `graveyard_count == 0` ignores the graveyard branch entirely.
- **Confidence:** high

## F-029: Duplicate `init_test_repo` helper drift in `audit_test.rs`
- **Severity:** high
- **Location:** `tests/audit_test.rs:13-28`
- **Description:** `audit_test.rs` defines its own `fn git(repo, args)` helper that duplicates `tests/common/mod.rs::run_git_checked` byte-for-byte but with a slightly different signature (takes `&Path`, uses `-C` explicitly). The file still does `mod common;` at line 1 and calls `common::init_test_repo(&root)` at line 39 — so both helpers coexist. Future fixes to `common::run_git_checked` (e.g. adding `GIT_CONFIG_GLOBAL=/dev/null` per F-009) will not apply to the local helper, diverging behaviour across files. Similar duplication at `tests/respawn_test.rs:22-29`.
- **Proposed remediation:** Extend `tests/common/mod.rs` with a public `git_in(repo: &Path, args: &[&str])` helper and delete the duplicates in `audit_test.rs` and `respawn_test.rs`. Consider also exporting `common::create_branch_with_commits` (currently private in `audit_test.rs:72-86`) because the `integrate_test.rs` setup helpers reinvent the same pattern.
- **Confidence:** high

## F-030: `events_test.rs` hand-rolls `setup_active_run` that silently diverges from `common::init_test_repo`
- **Severity:** high
- **Location:** `tests/events_test.rs:12-19`
- **Description:** Instead of calling `common::init_test_repo` + `commands::run::create_in`, this file hand-rolls the active-run scaffolding: `std::fs::create_dir_all(run_dir)` then `symlink("runs/test-run", active_link)`. It skips `commands::init::run_in` entirely, so the tests are not exercising the real `init` → `run create` pipeline — they're testing against a hand-constructed fixture that could silently drift from the production code path. If `commands::init` later writes additional marker files (e.g. a schema version in `config.json`) that the event emitter comes to rely on, these tests will keep passing while real usage breaks.
- **Proposed remediation:** Replace the hand-rolled `setup_active_run` with the canonical `common::init_test_repo` + `commands::init::run_in` + `commands::run::create_in` sequence used by every other test file. If the goal is a lighter-weight fixture, promote it to `common::mod` with a name that advertises what it skips (e.g. `common::bare_active_run_symlink_only(&tmp)`) and document why.
- **Confidence:** high

## F-031: `tail_returns_last_n` and `emit_writes_jsonl` assume sequential clock-ordered emits but do not verify ordering safety
- **Severity:** high
- **Location:** `tests/events_test.rs:23-75, 80-95`
- **Description:** `tail_returns_last_n` emits 10 events in a single-threaded loop and asserts `result[0].message == "event 8"` through `"event 10"`. The underlying `events::tail` presumably returns file lines in order. This test does not cover concurrent emits from multiple workers (the real use case — workers, watcher, and orchestrator all write to `events.jsonl` simultaneously). There is no test that two concurrent `emit_info` calls produce two valid JSONL lines (no torn writes, no interleaving within a line). `emit_writes_jsonl` asserts exactly 3 lines but does not assert the ordering matches emit ordering — if the file were reversed, the test would still pass.
- **Proposed remediation:** Add a concurrency test that spawns N threads each emitting M events, joins them, then asserts (a) the file has exactly N*M lines, (b) every line is valid JSON (no torn writes), (c) no line is empty, (d) no line contains a literal `}{` boundary. For existing tests, change the 3-line assertion to also verify the task_ids in order are `["001","002","003"]`.
- **Confidence:** medium

## F-032: `install_test::install_creates_symlink` checks symlink existence but not content through the link
- **Severity:** high
- **Location:** `tests/install_test.rs:5-22`
- **Description:** The test creates `skill_src/SKILL.md` with a specific frontmatter, installs it, then asserts `link.join("SKILL.md").exists()`. It never asserts the file *content* through the symlink matches what was written — so if `install` ever copies rather than symlinks but breaks the content (writes an empty file, or the wrong file), this test still passes because the file path exists. It does correctly assert `metadata.file_type().is_symlink()` which catches copy-vs-symlink, but not corruption of the symlink target. The broader pattern — create a file then check it exists without asserting content, permissions, or absence of stray files — appears across the suite.
- **Proposed remediation:** After `install_skill`, assert `std::fs::read_to_string(link.join("SKILL.md"))` equals the exact string written. Additionally, assert `std::fs::read_link(&link).unwrap().ends_with("skill/agentrc")`, and assert the skills directory contains *only* the expected entry by checking `std::fs::read_dir(&skills_dir).count() == 1`.
- **Confidence:** high

## F-033: Test-failure diagnostics assertion may leak child stdout into the stderr capture
- **Severity:** high
- **Location:** `tests/integrate_test.rs:323-360`
- **Description:** `test_failure_diagnostics_includes_stderr` writes a `config_snapshot` with `"test_command": "echo 'test error output' >&2 && exit 1"`. This depends on (a) a POSIX-compatible shell being invoked by `commands::integrate`, (b) `echo` being a builtin or on PATH, (c) `>&2` being parsed. On Windows this test would break. More importantly, no assertion is made about *where* the text came from; if the integrate implementation runs the command via a shell that merges streams and `test_stderr` ends up with the string because it was printed on stdout, the test still "passes" with a false positive. The test asserts on stderr but the fixture does not robustly *produce* stderr.
- **Proposed remediation:** Write a tiny helper shell script or use `std::process::Command` with explicit `stderr(Stdio::piped())` inside the production code and expose a test-only config hook. At minimum, also assert `test_stdout.is_none()` or that stdout does *not* contain `"test error output"` — this provably distinguishes the two streams. Add `#[cfg(unix)]` to this test.
- **Confidence:** medium

## F-034: CLI-only coverage for large subcommands — no fine-grained unit tests for `status::format_tty` helpers
- **Severity:** high
- **Location:** `tests/status_test.rs:119-296`, `tests/cli_smoke_test.rs:14-47`
- **Description:** `status_test.rs` tests ANSI colour codes, unicode status symbols (`✓ ● ◼`), and human-readable token summaries (`"45.2k"`, `"2 workers"`) by invoking the full `commands::status::format_tty(tmp.path())` pipeline which reads the filesystem, parses JSON, and renders. Several assertions exercise pure formatting functions (`format_tokens`, `format_duration`, symbol-for-state lookup) that could be unit-tested directly without any `TempDir`, git init, or `commands::init` call. The full-CLI assertion is slower (file I/O, JSON parse), more brittle (any column reorder breaks the substring search), and less precise. `cli_smoke_test.rs` is the only end-to-end `assert_cmd` coverage — no subcommand has a direct CLI test asserting stdout+stderr+exit code together.
- **Proposed remediation:** Extract status-rendering primitives into testable pure functions (`format_status_row(&TaskStatus) -> String`, `state_symbol(&TaskState) -> char`, `ansi_for_state(&TaskState) -> &str`) and add fast unit tests. Keep one or two end-to-end `format_tty` tests as integration smoke. Add per-subcommand `assert_cmd` tests that assert on `.stderr(…)` + `.stdout(…)` + `.code(…)` simultaneously.
- **Confidence:** high

## F-035: `status_displays_pane_title_over_raw_id` has a brittle negative assertion
- **Severity:** high
- **Location:** `tests/status_test.rs:122-146`
- **Description:** The test asserts `!output.contains("%42")` to prove the pane title is shown instead of the raw pane id. But the fixture `setup_run_with_tasks` also creates tasks 001 and 003 with no pane_id set — they cannot produce `%42` regardless. If a future refactor drops the pane_id from the pane_title fallback path for *all* tasks, this negative assertion still passes vacuously. Worse, the substring `"%42"` can collide with any future output containing `%4` followed by `2` (e.g. a percentage column, `42%` of anything).
- **Proposed remediation:** Change the negative check to a positive assertion: parse the rendered table, locate the row for task 002, and assert its pane cell equals `"orc:002:review-deps"` and not `"%42"`. If parsing the table is out of scope, at minimum use a longer unambiguous string such as `"%42 "` (with trailing space) or set pane_id on task 002 to a value like `%ZXCV99` that cannot plausibly collide.
- **Confidence:** high

## F-036: `format_tty` ANSI-colour assertions are fragile against NO_COLOR / terminfo
- **Severity:** high
- **Location:** `tests/status_test.rs:283-296`
- **Description:** `status_tty_contains_ansi` hard-codes `\x1b[38;2;` (24-bit RGB truecolor) and `\x1b[0m` reset as required substrings. It makes no attempt to unset `NO_COLOR`, `TERM`, or `CLICOLOR_FORCE` in the test environment. If `commands::status::format_tty` ever adopts the standard "respect `NO_COLOR=1`" convention, CI runs that happen to set `NO_COLOR` (some GitHub Actions runners do) will start failing this assertion with no actionable signal. The test also asserts `"\x1b[38;2;"` specifically, which means a fallback to 8-colour ANSI (`\x1b[3Xm`) would fail even though output is still correctly coloured.
- **Proposed remediation:** Make the test explicitly set the env it expects (`std::env::remove_var("NO_COLOR")` — but see F-001, that needs `#[serial]`), or pass an explicit `ColorChoice` parameter to `format_tty` and construct it with `Always` inside the test. Additionally, loosen the substring to `"\x1b["` (any CSI) rather than a specific RGB prefix, unless the intent is to assert truecolor specifically.
- **Confidence:** high

## F-037: `worker_heartbeat_updates_mtime` sleeps 50ms — flaky on coarse-resolution filesystems
- **Severity:** high
- **Location:** `tests/worker_commands_test.rs:131-141`
- **Description:** The test calls `heartbeat::tick`, records mtime, sleeps `Duration::from_millis(50)`, calls `tick` again, and asserts `mtime2 > mtime1`. Three failure modes: (a) filesystems with 1-second mtime granularity (FAT, some overlay mounts, macOS HFS+ with legacy settings) will observe equal mtimes after 50ms; (b) if the test is scheduled out for more than a few ms on a loaded CI runner, 50ms can still be insufficient on a slow NFS-backed `/tmp`; (c) the `>` comparison depends on `SystemTime` ordering which is well-defined on Linux but not guaranteed to advance monotonically across sleeps on all platforms.
- **Proposed remediation:** Remove the sleep. If the production code is supposed to touch mtime, add an API `tick_returning_time(&path) -> SystemTime` and assert the returned time advances. Alternatively, use `filetime::set_file_mtime` to set the first tick's mtime to a known value in the past, then tick and assert the new mtime is newer than that past value.
- **Confidence:** high

## F-038: `audit::audit_tdd` `classify_commit` — deleted-file and non-src/tests paths untested
- **Severity:** medium
- **Location:** `src/audit.rs:20-29`
- **Description:** Existing tests cover `tests/`-only, `src/`-only, and mixed. Untested: (a) empty files slice (returns `CommitKind::Impl` via fallthrough on line 27 — is that correct? A commit with no files classified as "Impl" seems wrong); (b) paths outside `src/` and `tests/` (e.g. `docs/`, `Cargo.toml`, `README.md`) — all currently classify as `Impl` via the fallthrough; (c) nested paths that contain `src/` or `tests/` without `starts_with` (e.g. `foo/src/x.rs`); (d) absolute paths (e.g. `/home/eric/src/x.rs`); (e) empty commits.
- **Proposed remediation:** Add `classify_empty_files_is_impl_or_other` (and fix the classifier to return a new `CommitKind::Other` or `Unknown` if the semantics are wrong); `classify_docs_only_commit_not_test`; `classify_cargo_toml_only_is_impl` (decide if correct); `classify_foo_src_x_is_impl`.
- **Confidence:** high

## F-039: `amend::replace_brief` error path for missing replacement file is untested
- **Severity:** medium
- **Location:** `src/commands/amend.rs:106-125`
- **Description:** `replace_brief` calls `std::fs::read_to_string(new_brief_file)` and bubbles up errors with a context string. No test passes a non-existent `--brief` path to `amend::run_in`; the existing test always supplies a real file. Also untested: a replacement file whose frontmatter is itself malformed (bubbles up from the first `upsert_field` call at line 121 via `split_frontmatter`), and a replacement file with no frontmatter at all — the silent fall-through through `upsert_field` would return an error, which has no assertion.
- **Proposed remediation:** Add two tests: (a) `amend::run_in(..., Some("/nonexistent.md"), None)` → `Err` with message containing "failed to read replacement brief", (b) replacement file that is plain markdown with no `---` block → `Err` (and confirm the original brief on disk is unchanged).
- **Confidence:** high

## F-040: `amend::run_in` does not reject clean/no-change inputs
- **Severity:** medium
- **Location:** `src/commands/amend.rs:22-102`
- **Description:** When `--brief` points to a file identical to the current brief, or `--message` is an empty string, `run_in` still writes the file, bumps `redispatch_count`, and sends a tmux notification. There is no "clean-tree-but-no-changes" guard. Because the result of serializing/writing an unchanged file still increments `redispatch_count`, a user can burn through their retry budget by issuing redundant amends. No test covers empty `--message` or noop `--brief`.
- **Proposed remediation:** Add a content-diff check before writing, and an explicit empty-message guard (return `AppError::EmptyAmendment`). Tests: (1) `Some("")` message → error, no increment; (2) brief file byte-identical to current → noop and error (or at least no redispatch bump).
- **Confidence:** medium

## F-041: `amend::run_in` silently swallows `update_field` errors if replacement has no matching system keys
- **Severity:** medium
- **Location:** `src/commands/amend.rs:113-123`
- **Description:** The loop iterates `SYSTEM_FIELDS` and calls `get_field` on the original, then `upsert_field` on the replacement. If the original lacks a field, that field is skipped; if `upsert_field` fails because the replacement has no frontmatter, `?` propagates — but no test writes a replacement that has no frontmatter (see F-039). More subtly, if the original has `pane_id` but the replacement lacks a frontmatter block entirely, the user loses all system fields silently. The ordering is correct but the untested error contract is fragile.
- **Proposed remediation:** Add a round-trip test: original has `pane_id: "%99"`, `worktree: X`, `created_at: T`; replacement has full frontmatter with different values; assert all three system fields in the result equal the original values. Also test with a replacement that only has `---\n---` (empty frontmatter).
- **Confidence:** medium

## F-042: `integrate_in` does not verify no merge is in progress before starting
- **Severity:** medium
- **Location:** `src/commands/integrate.rs:241-269`
- **Description:** If a previous integration was interrupted mid-merge (crash, Ctrl-C between `merge_no_ff` and `merge_abort`), `.git/MERGE_HEAD` still exists. The next `integrate_in` call will `checkout` (likely failing with "you need to resolve your current index first") but may also partially succeed depending on state. No test simulates "interrupted prior merge" by creating a `.git/MERGE_HEAD` file and calling `integrate_in`.
- **Proposed remediation:** Before checkout, check for in-progress merge (`.git/MERGE_HEAD` exists) and bail with `AppError::MergeInProgress`. Add a regression test.
- **Confidence:** medium

## F-043: `collect_writer_tasks_ordered` silently skips malformed briefs
- **Severity:** medium
- **Location:** `src/commands/integrate.rs:462-469`
- **Description:** When a `.md` file in `tasks/` has invalid frontmatter, the code prints `WARNING: skipping {name}: {e}` to stderr and continues. No test writes a syntactically-broken brief (missing closing `---`, invalid YAML indentation, non-UTF8 bytes) to confirm that: (a) the warning is actually emitted, (b) valid siblings still integrate, (c) the broken file is not silently treated as a writer and then crashed on later.
- **Proposed remediation:** Add a test that puts two briefs in `tasks/` — one valid writer, one corrupt — and asserts `integrate_in` returns a single-element result for the valid one and that stderr contains the warning.
- **Confidence:** high

## F-044: `commands::init::update_claude_md`, `load_claude_md_template`, `add_to_gitignore` helpers untested
- **Severity:** medium
- **Location:** `src/commands/init.rs:84-173`
- **Description:** The marker-replacement logic in `update_claude_md` (begin/end markers, replace-vs-append fork on line 100-121) is not directly tested. `load_claude_md_template` (which reads `~/.claude/skills/agentrc/claude-md-section.md`) has no test. `add_to_gitignore` is covered only through `init::run_in`; its edge cases (empty file, no trailing newline, blank lines inside existing content) are not asserted directly.
- **Proposed remediation:** Extract `update_claude_md_content(existing: &str, section: &str) -> String` as a pure function and add unit tests for: (a) empty existing, (b) existing without markers, (c) existing with markers mid-file, (d) existing with only begin marker (unclosed block preserves existing — currently line 107-109).
- **Confidence:** high

## F-045: `commands::install::find_repo_root`, `install_binary_symlink`, `run()` entry point untested
- **Severity:** medium
- **Location:** `src/commands/install.rs:6-51, 99-135, 150-163`
- **Description:** `tests/install_test.rs` covers `install_skill` and `check_command_exists`. The private `find_repo_root` walks up for `Cargo.toml` + `skill/` — its error branch (no parent) is not tested. `install_binary_symlink` is entirely untested (manipulates `~/.cargo/bin` and `~/.local/bin`). The `run()` CLI entry is untested. These are privileged filesystem operations that overwrite user symlinks; a regression could corrupt a user's `~/.local/bin`.
- **Proposed remediation:** Make `find_repo_root` `pub(crate)` and add `find_repo_root_walks_up`, `find_repo_root_errors_when_not_in_repo`. Either refactor `install_binary_symlink` to accept its paths as parameters (so it can be tested with a tempdir HOME) or extract a pure `compute_binary_link_targets` helper and test that.
- **Confidence:** high

## F-046: `setup_worktree` error when `git.create_worktree` fails is untested
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:59-79`
- **Description:** `create_worktree` fails when the branch name already exists, when the base ref doesn't exist, or when the worktrees dir is not a git repo. Only the "worktree path already exists" branch is reachable via `AppError::WorktreeExists`; no test provides an invalid base (e.g. `"nonexistent-branch"`) or a pre-existing branch name colliding with `branch`. The `.with_context(|| format!("failed to create worktree ..."))` wrapping is uncovered.
- **Proposed remediation:** Add tests: (1) base = "no-such-branch" → `Err` with context mentioning worktree, (2) pre-create branch "orc/001-foo" in the bare repo then call `setup_worktree` with the same branch name → `Err`.
- **Confidence:** high

## F-047: `spawn::find_task_brief` matches ambiguous prefixes non-deterministically
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:33-53`
- **Description:** The prefix match `name.starts_with("{task_id}-")` uses a trailing `-`, so `task_id = "1"` won't match `"10-foo.md"` — that's OK. However, the loop returns the FIRST match from `read_dir`, whose iteration order is filesystem-defined — if two briefs exist for the same id (e.g. `001-foo.md` and `001-bar.md` from a botched rename), one is silently chosen. No test covers duplicates or confirms the returned brief is deterministic.
- **Proposed remediation:** Detect the duplicate case and return `AppError::AmbiguousTaskBrief { task_id, matches: Vec<PathBuf> }`. Add a test that writes both files and asserts the error.
- **Confidence:** medium

## F-048: `spawn::run` clobbers brief `pane_id` without a lock
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:177-180`
- **Description:** The sequence `read_to_string(&brief_path) → frontmatter::update_field → write(&brief_path)` is non-atomic. If the orchestrator issues two concurrent spawns for different tasks (different IDs, same file isn't written), no harm. But if a spawn races with an `amend` (which also reads-modifies-writes the brief at `amend.rs:67-82`), one write can clobber the other's. No concurrency test covers this.
- **Proposed remediation:** Serialize brief-file writes via a per-file lock, or adopt atomic tempfile+rename. Add a concurrency regression test where one thread calls `amend::run_in` and another calls a refactored `update_pane_id(&brief_path, "%12")` and asserts both effects are visible.
- **Confidence:** medium

## F-049: `spawn::run` status-patch is non-atomic and uncovered
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:183-191`
- **Description:** After `write_initial_status`, spawn re-reads the status file, mutates `pane_id`/`pane_title`, and writes it back. Any concurrent `worker::status::run_in` call (e.g. the worker racing ahead to emit a `spawning` status with `started_at`) loses one update. `worker::status::run_in` itself is a read-modify-write (`status.rs:46-105`). No test covers the spawn↔worker-status race.
- **Proposed remediation:** Use atomic writes (tempfile + rename) and include a version counter, or serialize status writes behind a file lock. Multi-thread test asserts monotonic phase_history regardless of interleaving.
- **Confidence:** high

## F-050: `respawn::run_in` does not handle `remove_worktree` failure gracefully
- **Severity:** medium
- **Location:** `src/commands/respawn.rs:54-59`
- **Description:** When the old worktree exists but is locked (e.g. another process has a file open, or the user cwd'd into it in another shell), `git worktree remove --force` can still fail, bubbling up with context. The failure is then interleaved: the old pane has been killed but no new worktree was created and no status was written. The task is left in a half-respawned state. No test covers this recovery gap.
- **Proposed remediation:** Either (a) move the kill_pane AFTER the worktree work, so a failed worktree removal leaves the old pane alive, or (b) emit a clear AppError identifying the orphan state, and test the recovery by making the worktree path read-only.
- **Confidence:** medium

## F-051: `process_status_change` silently returns `None` on malformed JSON
- **Severity:** medium
- **Location:** `src/commands/watch.rs:18-43`
- **Description:** Both `read_to_string` and `from_str` errors are converted to `None` via `.ok()?`. A malformed status JSON is indistinguishable from "nothing changed" from the watcher's POV — no warning is printed, no log emitted. If a worker writes a partial status (F-054-style) the watcher silently drops the event. No test passes a `.json` file with invalid content to `process_status_change` to confirm the `None` behavior; the contract is undocumented.
- **Proposed remediation:** Surface errors as a warning line (e.g. `"[HH:MM:SS] WARNING: could not parse {path}: {e}"`) rather than silently dropping. Add a test that passes a path containing `"not json"` and asserts a `Some(...)` warning output (or at minimum, document and test that `None` is returned).
- **Confidence:** high

## F-052: `check_heartbeat_staleness` clock-skew / future-mtime case is untested
- **Severity:** medium
- **Location:** `src/commands/watch.rs:47-62`
- **Description:** `SystemTime::now().duration_since(modified)` returns `Err` if `modified > now` (clock skew, VM pause, NTP adjustment, or a test that calls `filetime::set_file_mtime` with a future time). The function silently returns `None` (no warning), which is arguably correct, but untested. On some filesystems (SMB/NFS) this is a common real-world case.
- **Proposed remediation:** Add a test that sets `mtime` to `now + 60s` and asserts `None` is returned (healthy). Consider explicitly handling the future case with `unwrap_or(Duration::ZERO)` so the function is total.
- **Confidence:** medium

## F-053: `worker::heartbeat::tick` after `done` is silently accepted
- **Severity:** medium
- **Location:** `src/commands/worker/heartbeat.rs:21-36`
- **Description:** `tick` unconditionally touches the heartbeat file. A crashed-then-restarted worker whose parent task is already `completed` will happily continue updating the alive file, and `find_stale_heartbeats` / `watch` have no way to tell the heartbeat is zombie. No test exercises "heartbeat after completed". The heartbeat daemon loop at `heartbeat.rs:14-18` also has no graceful-shutdown or exit condition — it runs forever until killed, even after the task completes.
- **Proposed remediation:** In `tick`, read the status file (best-effort); if state is terminal (`Completed|Failed|Aborted`), delete the heartbeat file and return `Ok(())` without re-creating it. Have `run()` exit the loop in that case. Add a test that sets status to completed, runs `tick`, and asserts no heartbeat file exists.
- **Confidence:** medium

## F-054: Heartbeat file fsync / partial-write race is not exercised
- **Severity:** medium
- **Location:** `src/commands/worker/heartbeat.rs:26-34`
- **Description:** `OpenOptions::new().create(true).truncate(true).write(true).open(...)` followed by `f.set_len(0)` is not atomic from the perspective of `watch::check_heartbeat_staleness` running concurrently. Between the `open` (which truncates to 0) and any subsequent write there is a window where the file exists with mtime updated but potentially zero-length; readers reading the mtime see a fresh timestamp, which is fine, but if a future change ever writes a body (e.g. PID), concurrent readers may read a truncated file. No concurrency test covers this race.
- **Proposed remediation:** Write heartbeat atomically via tempfile + rename (`tempfile::NamedTempFile::new_in(dir)?.persist(path)`), and add a multi-thread test that spawns 32 concurrent `tick` calls and 32 concurrent `check_heartbeat_staleness` calls and asserts no torn reads / no IO errors.
- **Confidence:** medium

## F-055: `worker::note::run_in` is not atomic; interleaved writers corrupt notes
- **Severity:** medium
- **Location:** `src/commands/worker/note.rs:21-42`
- **Description:** The pattern "read full file → append in memory → write full file" is racy: two concurrent `note` invocations for the same `task_id` will each read the file, each append their entry, and each write — the second overwrites the first's entry. This is a classic file-event-bus hazard called out in the audit scope. No test exercises concurrent note-writers; tests only assert sequential appends.
- **Proposed remediation:** Use `OpenOptions::new().append(true).create(true).open(...)` to get atomic append on POSIX, or wrap the whole read-append-write in a file lock (`fs2` crate). Add a multi-thread test that spawns 16 `run_in` calls and asserts all 16 entries are present and well-formed.
- **Confidence:** high

## F-056: `commands::worker::resolve_project_root` fallback path untested
- **Severity:** medium
- **Location:** `src/commands/worker/mod.rs:18-23`
- **Description:** The `AGENTRC_PROJECT_ROOT` env-var branch and the cwd-fallback branch are both public behaviours of worker subcommands, but no test asserts either path. Every test calls `*::run_in(project_root, …)` directly, bypassing `resolve_project_root`. A regression that swaps the precedence or mis-parses the env var will go undetected until workers run in worktrees.
- **Proposed remediation:** Add `tests/worker_commands_test.rs` cases: `resolve_project_root_uses_env_var_when_set` (sets env var via `std::env::set_var` inside a `serial_test`-style guard — see F-001), and `resolve_project_root_falls_back_to_cwd`.
- **Confidence:** high

## F-057: `detect_from_text` has gaps for several documented priority rules
- **Severity:** medium
- **Location:** `src/detect/mod.rs:51-107` (also `scan_pane`/`scan_pane_full` at `164-183` and `DetectedState::Display`/`icon` at `32-46`)
- **Description:** `tests/detect_test.rs` covers most priorities but misses: (a) the `(lower.contains("allow") && lower.contains("permission"))` disjunct on line 58 — only `"do you want to proceed"` is tested; (b) the `"overloaded"` rate-limit keyword (line 64); (c) the `"sigterm"`, `"sigsegv"`, `"fatal error"` error keywords (lines 70-72) — only `"panicked at"` is tested; (d) `edit(` case on line 86; (e) `"cargo test"` Running branch (line 94); (f) `"npm "` Running branch (line 95); (g) the `trimmed.ends_with("> ")` alternative idle marker (line 102); (h) `scan_pane` / `scan_pane_full` — the `Dead` fallback on error — have zero tests. Additionally, `DetectedState::fmt` and `icon()` (9-arm matches) are never exhaustively asserted.
- **Proposed remediation:** Add detect tests covering each missing keyword: `detect_needs_input_allow_permission`, `detect_rate_limited_overloaded`, `detect_errored_sigterm`, `detect_errored_fatal_error`, `detect_tool_use_edit_paren`, `detect_running_cargo_test`, `detect_running_npm`, `detect_idle_gt_space`. For `scan_pane{,_full}` run against a non-existent pane id and assert `DetectedState::Dead`. Add `detect_icon_exhaustive` and `detect_display_exhaustive` asserting each of the 9 variants maps to its documented string.
- **Confidence:** high

## F-058: `fs::bus::OrchestratorPaths::active_run` untested edge cases (absolute symlink + broken symlink)
- **Severity:** medium
- **Location:** `src/fs/bus.rs:50-59`
- **Description:** Two gaps: (a) `active_run` handles both relative and absolute symlink targets, but `tests/fs_test.rs::active_run_follows_symlink` only tests the relative form (`"runs/test-run"`); the `else { target }` branch (line 56) for absolute symlink targets is untested; (b) `read_link` only fails if the link itself doesn't exist — a broken symlink (target removed) returns `Ok(target)` and `active_run` returns `Some(RunPaths { root: <nonexistent path> })`. Every downstream `is_dir()` check then returns false and the caller gets "no tasks" behavior, but `active_run` itself claims success. `tests/fs_test.rs::active_run_returns_none_when_no_symlink` covers "no link" only.
- **Proposed remediation:** Add `active_run_follows_absolute_symlink` that creates the symlink with an absolute target path and verifies resolution. Verify the resolved path `is_dir()` before returning `Some(...)`, or return an explicit `Result<Option<RunPaths>, AppError>` differentiating the failure modes. Add tests for: (a) symlink → deleted target, (b) symlink → regular file.
- **Confidence:** high

## F-059: `frontmatter::parse` accepts missing-closing-delim edge cases inconsistently
- **Severity:** medium
- **Location:** `src/fs/frontmatter.rs:9-29`
- **Description:** `split_frontmatter` requires a literal `"\n---"` close sequence via `after_open.find("\n---")`. That means a document whose closing delimiter is the very first line after the opening (e.g. `"---\n---"` — empty frontmatter) returns "missing closing frontmatter delimiter" because `after_open` starts after stripping the `\n` from the opener. Similarly, `"---\r\n...\r\n---"` (CRLF line endings from Windows) will not match because the search is for literal `\n---`. Neither case is tested.
- **Proposed remediation:** Change the search to match `"---"` at line-start rather than relying on a leading `\n`, and normalize CRLF. Add tests for: (a) empty frontmatter `"---\n---\nbody"`, (b) CRLF content, (c) frontmatter whose closing `---` has trailing whitespace (`"---   "`).
- **Confidence:** high

## F-060: `frontmatter::update_field` succeeds on malformed YAML as long as the key literal appears
- **Severity:** medium
- **Location:** `src/fs/frontmatter.rs:55-81`
- **Description:** `update_field` is a line-oriented textual substitution — it does not parse YAML. It matches any line whose trimmed prefix is `"{key}:"` or `"{key} :"`. This means: (a) a nested key under another mapping (`"metadata:\n  pane_id: foo"`) is wrongly rewritten at the nested location, and (b) a multi-line string value with `pane_id:` embedded as content is corrupted. No test covers nested keys or multi-line scalars. Also, the `yaml_safe_value` escape list does not include `\n` / `\t`, so a newline in the value produces invalid YAML silently.
- **Proposed remediation:** Add tests covering nested-key and block-scalar YAML; if line-based editing is intentional, document it and add a guard that bails when the parsed YAML before/after differs in unexpected keys. Also reject `\n` in values with a helpful error.
- **Confidence:** high

## F-061: `fs::run::RunPaths::run_id()` fallback to "unknown" untested
- **Severity:** medium
- **Location:** `src/fs/run.rs:23-28`
- **Description:** The `unwrap_or("unknown")` fallback (line 27) for when the file_name is not UTF-8 or is empty is never asserted. Used in `checkpoint::save_in` to populate `Checkpoint.run_id`. Unlikely in practice but a silent failure mode.
- **Proposed remediation:** Add `run_paths_run_id_returns_directory_name` and `run_paths_run_id_fallback_for_empty_path` to `tests/fs_test.rs`.
- **Confidence:** medium

## F-062: `OrchestratorConfig` forward/backward-compat serde tests missing
- **Severity:** medium
- **Location:** `src/model/config.rs:24-71`
- **Description:** `config_json_roundtrip` covers only the fully-populated happy case. The config uses `#[serde(default = ...)]` on 7 fields so old configs missing those fields should deserialize — no test asserts this. In particular: (a) a minimal config with only `project_root` should parse and use all defaults; (b) a config with unknown future fields should ignore them (no `deny_unknown_fields` — good, but untested); (c) the `worker_claude_args: Vec<String>` default of `[]`; (d) if `max_workers` overflows `u32` in JSON the error message should be useful.
- **Proposed remediation:** Add `config_backward_compat_minimal` (just `{"project_root":"."}` deserializes with defaults), `config_ignores_unknown_fields`, `config_rejects_negative_max_workers_with_clear_error`. Keep the existing round-trip test.
- **Confidence:** high

## F-063: `OrcEvent`/`EventType` exhaustive serde-variant coverage is missing
- **Severity:** medium
- **Location:** `src/model/event.rs:13-34`
- **Description:** `EventType` has 18 variants. `events_test.rs::event_serialization_roundtrip` tests exactly one variant (`MergeConflict`). `widgets::events::event_type_label` has an exhaustive match but isn't pinned by test. A rename (e.g. `CheckpointSaved` → `Checkpointed`) would silently break JSONL log backward compatibility because existing on-disk events would fail to deserialize. `Severity` has 3 variants; only `Info` (via `emit_info`) is round-tripped in integration tests.
- **Proposed remediation:** Add `event_type_serde_exhaustive_roundtrip` that iterates a `const` array of all 18 variants and round-trips each through JSON, asserting the resulting `serde_json::Value` string key matches the documented `snake_case` name. Same for `Severity`. Also add `event_type_snake_case_wire_format` pinning exact strings for 2-3 canonical variants as a backward-compat firewall.
- **Confidence:** high

## F-064: `TaskState::can_transition_to` — exhaustive transition matrix untested
- **Severity:** medium
- **Location:** `src/model/task.rs:24-42`
- **Description:** `tests/model_test.rs::task_state_valid_transitions` asserts 7 valid transitions and 2 invalid ones (`Completed→InProgress`, `Failed→InProgress`). The rejection matrix is much larger — e.g. `Aborted→anything`, `Completed→anything`, `Ready→Completed`, `Blocked→Completed`, `Spawning→InProgress`, reflexive self-transitions, the new `Blocked → Failed`/`Blocked → Aborted` (lines 38-39), and `Ready → Aborted`. None of these are tested. Note that `AppError::InvalidStateTransition` is defined but never actually returned from any call site, so this function's result is informational-only today; F-007 raised the dead-code concern.
- **Proposed remediation:** Add `task_state_transition_matrix` that iterates `[Spawning, Ready, InProgress, Blocked, Completed, Failed, Aborted]²` and asserts `can_transition_to` against a ground-truth set, failing with a clear message listing all mismatches.
- **Confidence:** high

## F-065: Tmux instance-method error paths (non-zero exit, non-UTF-8 stdout) are untested
- **Severity:** medium
- **Location:** `src/tmux/wrapper.rs:142-160` (`run_tmux`) and callers
- **Description:** `tests/tmux_test.rs` covers exclusively the static `build_*_args` functions — there is no coverage of `run_tmux` / `split_window` / `capture_pane` / `kill_pane` / `list_panes_with_titles` or any instance method. Specific untested semantics: (a) tmux binary not on PATH → `.context("failed to execute tmux")` (line 146); (b) tmux exits non-zero → formatted `bail!` message containing `args.join(" ")`, exit status, and stderr trim (lines 148-155); (c) non-UTF-8 stdout handled by `String::from_utf8_lossy` (line 158); (d) `list_panes_with_titles` output parser on lines 267-273 — the `splitn(2, '\t')` handles titles containing tabs by only splitting on the first, but this is never asserted. Empty-line filtering (line 266) is untested.
- **Proposed remediation:** Add integration tests gated on `tmux` availability: `tmux_capture_pane_nonexistent_pane_returns_err_with_stderr`, `tmux_kill_pane_nonexistent_returns_err`, `tmux_list_panes_empty_window_returns_empty_vec`. Extract `parse_list_panes_output(s: &str) -> Vec<(String,String)>` as a pure helper and unit-test it with: empty string, single line without tab, single line with multiple tabs, trailing newline, interior empty lines.
- **Confidence:** high

## F-066: `widgets::events::render` untested for overflow, wrapping, and special-char messages
- **Severity:** medium
- **Location:** `src/tui/widgets/events.rs:40-87`
- **Description:** The inline tests cover only the happy path with three short events in an 80-wide buffer and the empty case. Uncovered: (a) more events than the panel can fit; (b) message with embedded newlines or control chars; (c) over-wide `task_id` or `message` in a narrow area; (d) every `EventType` variant's label is never exhaustively checked — only `Spawned`, `Failed`, `NeedsInput` are probed; (e) `Severity::Error` color path is untested. `event_type_label` is a pure function trivially testable standalone.
- **Proposed remediation:** Add `event_type_label_exhaustive` test mapping every `EventType` variant to its expected string. Add `events_panel_narrow_area` and `events_panel_many_events` rendering tests asserting no panic and that the title is still present. Add a `severity_color_error_is_err_theme` test.
- **Confidence:** high

## F-067: `widgets::table::state_symbol`, `state_color`, `activity_symbol`, `activity_color`, `build_row`, `is_graveyard` untested
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:20-69, 71-76, 78-197`
- **Description:** Six private pure functions encode the visual contract of every worker row and are untested. In particular: (a) the 7-variant `state_symbol` match — if a new `TaskState` variant is added, nothing fails at compile time; (b) `activity_symbol`/`activity_color` cover 9 `DetectedState` variants each — none asserted; (c) `build_row` contains significant logic: token-ratio color thresholds (`0.8` → ERR, `0.5` → WARN), elapsed-time formatting branches, pane fallback chain `pane_title → pane_id → "-"`, stale-heartbeat style override, graveyard dimming.
- **Proposed remediation:** Expose helpers as `pub(crate)` and add unit tests: `state_symbol_for_each_variant`, `activity_color_needs_input_is_err`, `build_row_elapsed_formats_seconds_minutes_hours`, `build_row_token_color_crosses_thresholds` (ratios 0.4/0.6/0.9), `build_row_pane_fallback_chain`, `build_row_graveyard_uses_dim_modifier`, `build_row_stale_heartbeat_uses_warn_color`.
- **Confidence:** high

## F-068: `widgets::table::render_workers` / `render_graveyard` never rendered in a unit test
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:221-274, 276-329`
- **Description:** The two main table renderers have no direct test coverage. `dashboard_test.rs` constructs an `App` and checks counts but never calls `render_workers`/`render_graveyard`. Missing coverage: (a) empty `statuses` → should produce a bordered but empty table without panicking; (b) `statuses` longer than available area rows; (c) terminal resize: running with `area.width == 0` or `area.height == 0`; (d) overlong `pane_title` / `branch` / `last_message` strings; (e) mixed `selected` index straddling active / graveyard boundary.
- **Proposed remediation:** Add `tests/table_render_test.rs` (or inline) with: `render_workers_empty_state_no_panic`, `render_workers_many_workers_no_clip_panic`, `render_workers_narrow_area`, `render_workers_zero_area`, `render_graveyard_selected_index_past_active`, `render_graveyard_selected_before_active_shows_no_selection`, `render_workers_overlong_pane_title`.
- **Confidence:** high

## F-069: `ui::render` and all layout math for terminal resize are untested
- **Severity:** medium
- **Location:** `src/tui/ui.rs:35-121`
- **Description:** The central `render` function composes the full dashboard layout and is never invoked under test. `anim_height` is thoroughly tested, but the `graveyard_height` calculation (`(graveyard_count as u16 + 3).min(area.height / 4)` at line 57) is not — specifically the `min(area.height / 4)` clamp for tiny terminals. The `Layout::default().constraints([…])` with 7 constraints can fail to satisfy on small heights, and there is no test that `render` is panic-free on a buffer as small as 10×5. The `show_help` overlay path and conditional `show_animation` / `show_events` combinations are uncovered.
- **Proposed remediation:** Add `tests/ui_render_test.rs` that builds a minimal `App`, renders into `Buffer::empty(Rect::new(0,0,W,H))` for several `(W, H)` combinations — 40×10, 80×24, 120×40, 200×80 — and asserts no panic plus the presence of key literal text ("agentrc", "Workers", "Graveyard", "Detail"). Include one case with `show_help = true`. Include one case with `show_events = false` and `show_animation = false`.
- **Confidence:** high

## F-070: `App::new` config parse failure and active-run-missing paths are untested
- **Severity:** medium
- **Location:** `src/tui/app.rs:45-98`
- **Description:** `App::new` has three error-return points: `std::fs::read_to_string` on the config (line 49), `serde_json::from_str` parse (line 50), and implicit failures in `refresh` (line 96). The existing `dashboard_test.rs::dashboard_app_loads_with_active_run` only covers the happy path. Untested: (a) a malformed config file returns the `"failed to parse config"` error; (b) project root without `.orchestrator/active` symlink falls back to `run_id = "none"` (line 58) without error; (c) `TMUX_PANE` env var set but `tmux list_panes_with_titles` fails — `orchestrator_pane` should silently become `None`; (d) `TMUX_PANE` set and list returns only the dashboard pane itself — `find` should yield `None`.
- **Proposed remediation:** Add integration tests: `dashboard_app_malformed_config_errors`, `dashboard_app_no_active_run_uses_none_run_id`, `dashboard_app_without_tmux_env_has_no_orc_pane`. Environment-variable tests must use a scoped mutex or `serial_test`.
- **Confidence:** high

## F-071: `cli_smoke_test::binary_has_subcommands` does a substring search that can match help text prose
- **Severity:** medium
- **Location:** `tests/cli_smoke_test.rs:25-47`
- **Description:** The test asserts `stdout.contains(subcmd)` for each of `["init","install","spawn","status","teardown","integrate","layout","resume","plan","run","worker"]`. Words like `"run"`, `"status"`, and `"init"` are generic enough to appear in clap's default help text prose and subcommand short descriptions. The test can pass even if the *subcommand* is silently dropped from the CLI, as long as the word appears somewhere in `--help`. Brittle-in-the-opposite-way: a future subcommand described with "run" in its help short trivially satisfies the assertion.
- **Proposed remediation:** Parse clap's help output for the `Commands:` section and assert each expected subcommand is a line-prefix match (`^\s+<subcmd>\b`). Or drive off `agentrc <subcmd> --help` returning exit 0 for each expected subcommand.
- **Confidence:** high

## F-072: `fault_stale_heartbeat_detection` mutates mtime but does not assert heartbeat file pre-existed
- **Severity:** medium
- **Location:** `tests/fault_injection.rs:115-128`
- **Description:** The test calls `worker::heartbeat::tick(tmp.path(), "001")` which creates the file, then backdates its mtime to 300s ago, then asserts staleness. It does not assert the tick *actually created the file* before the backdating step — if `tick` silently fails, `filetime::set_file_mtime` will panic rather than give an actionable error, and the test will report the wrong failure reason.
- **Proposed remediation:** After `tick`, add `assert!(hb.exists(), "tick should have created heartbeat file")` before calling `set_file_mtime`. Alternatively, change `tick` to return the created path and consume that path.
- **Confidence:** high

## F-073: `happy_path.rs::e2e_*` tests fan out to 40+ lines of setup with no reusable fixture
- **Severity:** medium
- **Location:** `tests/happy_path.rs:12-94, 97-142, 145-193, 196-243` (and related in `tests/amend_test.rs`, `tests/spawn_test.rs`, `tests/respawn_test.rs`, `tests/fault_injection.rs`, `tests/integrate_test.rs`)
- **Description:** All four e2e tests inline near-identical setup: `init_test_repo` → `init::run_in` → `run::create_in` → get `paths`, `active`, `git`, `base` → format a brief string → `spawn::setup_worktree` → `write_initial_status` → `worker::status::run_in`. The `format!` brief-builder is duplicated 5+ times with the same 8-field schema, plus the same template appears in `tests/amend_test.rs:16-34`, `tests/spawn_test.rs:15-28`, `tests/respawn_test.rs:32`, `tests/fault_injection.rs:60-63`, and `tests/integrate_test.rs:36-46,88-96,161-170` — at least 10 copies across the tree. If the frontmatter schema changes, you must update all sites.
- **Proposed remediation:** Extend `tests/common/mod.rs` with `fn writer_brief(id, slug, base_branch, deps) -> String` and `fn reader_brief(id, slug, base_branch, deps) -> String` that return fully-formed frontmatter+body strings. Replace every `format!("---\nid…")` call site with a one-liner. Add a `fn seed_writer_task(tmp, paths, id, slug)` helper that does the full init+run+brief+worktree+status dance since that sequence appears ~8 times.
- **Confidence:** high

## F-074: `format_duration_negative_returns_zero` tests a pure function but lives in an integration binary
- **Severity:** medium
- **Location:** `tests/status_test.rs:89-117`
- **Description:** The `format_duration` tests are pure — no TempDir, no git init — yet they live in `status_test.rs` which is one of the slowest test binaries because its other tests spin up git repos. When `format_duration_*` fails, the developer must wait for the rest of the file to build and execute. Representative of the broader unit-vs-integration imbalance.
- **Proposed remediation:** Move pure-function tests for `format_duration`, `format_tokens`, and similar rendering primitives into `#[cfg(test)] mod tests { … }` inside `src/commands/status.rs` (or `src/tui/widgets/table.rs`). Keep integration-scope tests (that need TempDir + git) in `tests/status_test.rs`.
- **Confidence:** high

## F-075: `status_tty_contains_symbols` hardcodes Unicode glyphs but doesn't verify per-state mapping
- **Severity:** medium
- **Location:** `tests/status_test.rs:264-281`
- **Description:** The assertion is "completed → ✓, in_progress → ●, blocked → ◼" via three `output.contains(…)` checks. But with three tasks in three different states, the test does not prove *which* task got which glyph — the output could emit ✓ for `in_progress` and ● for `completed` (swapped) and still pass.
- **Proposed remediation:** Assert that the line containing task id `001` (completed) contains `✓`, the line with `002` (in_progress) contains `●`, and the line with `003` (blocked) contains `◼`. A regex per-row, or parsing the output into `Vec<Row>`, would make this watertight.
- **Confidence:** high

## F-076: `teardown_all_skips_in_progress_tasks` asserts nothing meaningful
- **Severity:** medium
- **Location:** `tests/teardown_test.rs:74-81`
- **Description:** Body ends with the comment "No assertion on 002's worktree since it has none, just verify no error". The test only proves `teardown_all` returns `Ok`. It does not prove 001's worktree was torn down, 002's status remained `in_progress`, or that `teardown_all` even *attempted* to look at either task. The test name promises behaviour the body does not verify.
- **Proposed remediation:** Add positive assertions: 001's worktree is gone (`!active.worktree_dir("001").exists()`), 002's status file still reads `in_progress`, and optionally a returned report from `teardown_all` enumerating which tasks were skipped with reason.
- **Confidence:** high

## F-077: `tmux_is_inside_checks_env` reads `TMUX` without isolation — parallelism hazard and no signal
- **Severity:** medium
- **Location:** `tests/tmux_test.rs:29-34`
- **Description:** The test comment says "TMUX env var may or may not be set depending on test context. Just verify the function exists and returns a bool." The test calls `Tmux::is_inside_tmux()` and discards the result — so it is literally a no-op except for a compile-check. If in the future this test or a peer calls `env::set_var("TMUX", "x")` and another test reads `TMUX` concurrently, a race will surface. The test provides zero coverage.
- **Proposed remediation:** Either delete the test or replace it with two `#[serial]`-annotated tests (requires F-001): one that sets `TMUX=something` and asserts `is_inside_tmux() == true`, and one that removes `TMUX` and asserts `false`. Save/restore the original value.
- **Confidence:** high

## F-078: `watch_test::heartbeat_stale_produces_warning` allows age window `"300" || "29"`
- **Severity:** medium
- **Location:** `tests/watch_test.rs:85-90`
- **Description:** The assertion is `warning.contains("300") || warning.contains("29")`. If `warning` is `"stale for 29,999 seconds"` or `"event 29"` or any string containing "29", the test passes. Combined with the hardcoded `300`-second staleness from `old_time`, the intent is presumably "age ≈ 300 seconds" — which should be asserted as a range, not a substring.
- **Proposed remediation:** Use a regex or parse the age out of the warning and assert a numeric range: `let age = parse_age(&warning); assert!((290..=310).contains(&age))`. This is resilient against minor clock skew and does not match random "29"s.
- **Confidence:** high

## F-079: `commands::events::run` and `commands::audit::run` CLI wrappers untested
- **Severity:** low
- **Location:** `src/commands/events.rs:5-29`, `src/commands/audit.rs:5-21`
- **Description:** Both modules expose only a `run()` CLI wrapper that reads cwd, calls into the underlying `events::tail` or `audit::audit_tdd`, and prints formatted output. No test covers the CLI-level printing (formatting of event lines, `No events.` message on empty log, `YES`/`NO` compliance label). These are thin wrappers, but regressions in output format break downstream scripts that parse them.
- **Proposed remediation:** Use `assert_cmd` (already used in `tests/cli_smoke_test.rs`) to invoke `agentrc events` and `agentrc audit 001` against a tempdir and assert on stdout contains/does-not-contain key markers.
- **Confidence:** medium

## F-080: `amend` pane-notification and `checkpoint::save_in` event emission unasserted
- **Severity:** low
- **Location:** `src/commands/amend.rs:91-100`, `src/commands/checkpoint.rs:142-147`
- **Description:** `amend::run_in` attempts a tmux `send_keys` to notify the worker of the amendment (best-effort). `checkpoint::save_in` emits a `CheckpointSaved` event after writing the file. Both side effects are not asserted in their respective tests.
- **Proposed remediation:** Add `checkpoint_save_emits_checkpoint_saved_event` to `tests/checkpoint_test.rs`. For amend's tmux call, it's truly best-effort and hard to test without a mock seam — document it as a known gap.
- **Confidence:** high

## F-081: `checkpoint::save_in` config-loading inconsistency with integrate
- **Severity:** low
- **Location:** `src/commands/checkpoint.rs:59-65`
- **Description:** `save_in` falls back to `OrchestratorConfig::default()` when `.orchestrator/config.json` is missing, but does NOT consult the run-level snapshot (`active.config_snapshot()`). In contrast, `integrate.rs::load_config` (line 423-436) prefers the snapshot. This inconsistency means `base_branch` in a saved checkpoint can disagree with `base_branch` used by integrate in the same run. Not tested.
- **Proposed remediation:** Unify config loading (extract a single `load_config(project_root, active) -> Result<OrchestratorConfig>`) and call it from both commands. Test: save checkpoint → base_branch equals snapshot value when both exist.
- **Confidence:** medium

## F-082: `commands::dashboard::run` has no smoke test (unavoidable: needs TTY)
- **Severity:** low
- **Location:** `src/commands/dashboard.rs:20-130`
- **Description:** The TUI entry point is genuinely untestable without a PTY harness; `tests/dashboard_test.rs` instead covers `App::new`, navigation, token aggregation, and token formatting — the testable business logic. The `run()` function itself (terminal setup, event loop, shell-escape handling on `Action::Shell`, mouse dispatch, alt-screen restoration) is not covered.
- **Proposed remediation:** No change required. Consider extracting the key-to-action mapping (already in `tui::action::handle_key`) and the `Action::Shell` branch's command-invocation logic into a pure function that can be unit tested.
- **Confidence:** high

## F-083: `append_log` silently drops all IO errors
- **Severity:** low
- **Location:** `src/commands/integrate.rs:515-524`
- **Description:** `append_log` uses `if let Ok(...)` and `let _ = writeln!`, swallowing both open and write failures. If the `.orchestrator/active/integration.log` path is not writable, diagnostics for conflicts and test failures are silently dropped — the user sees a summary in the terminal but no persistent record. Not tested.
- **Proposed remediation:** Surface log failures as a warning to stderr (one per session, not per line) and add a test that creates `integration.log` as a read-only file, runs integrate, and asserts a warning is emitted to stderr.
- **Confidence:** medium

## F-084: `integrate::run` CLI dry-run vs. real-run divergence is untested
- **Severity:** low
- **Location:** `src/commands/integrate.rs:63-68, 128-163`
- **Description:** The CLI entry `run(dry_run: bool)` forks to `run_dry_run` or `integrate_in`. No test asserts that dry-run output matches the real-run plan for the same setup. If `dry_run_in` and `integrate_in` ever drifted apart in how they collect/sort tasks, users would see misleading previews. Currently both call `collect_writer_tasks_ordered` — incidental, not guaranteed by a test.
- **Proposed remediation:** Add a property-style test: build a fixture with N writer tasks, call `dry_run_in` and `integrate_in`, and assert task_ids and branches appear in the same order with matching changed_files.
- **Confidence:** medium

## F-085: `layout::run` CLI mode-dispatch (including bail branch) has no direct test
- **Severity:** low
- **Location:** `src/commands/layout.rs:77-108`
- **Description:** `compute_collation` is thoroughly unit-tested. The CLI `run("tile" | "collate" | _)` dispatcher is not, including the `bail!("unknown layout mode: {}", mode)` error path (line 82). Similarly `load_config()` (line 97-108) reads/parses config with no direct test, and its `OrchestratorConfig::default()` fallback is only exercised when running without a config.
- **Proposed remediation:** Add `layout_run_unknown_mode_returns_error` and `load_config_falls_back_to_default_when_missing`. Expose `load_config` as `pub(crate)` if needed.
- **Confidence:** medium

## F-086: `respawn::run_in` pane-kill of dead pane is untested
- **Severity:** low
- **Location:** `src/commands/respawn.rs:49-52`
- **Description:** The `tmux.kill_pane(pane_id)` call is `let _ = ...`-swallowed — correct behavior because the pane may already be dead. But there is no test that asserts: (a) a stale `pane_id` does not abort the respawn, (b) `kill_pane` errors are NOT surfaced to the user. Since `run_in` also requires a live tmux server for subsequent calls, the function as-a-whole is untested.
- **Proposed remediation:** Factor the pre-tmux work (validate, kill stale pane, remove worktree, recreate worktree) into a `prepare_respawn` helper that doesn't touch tmux, then write tests for that helper.
- **Confidence:** medium

## F-088: `watch_with_receiver` ignores non-JSON files but that path is untested
- **Severity:** low
- **Location:** `src/commands/watch.rs:148-163`
- **Description:** The loop checks `path.extension() == Some("json")` for status events and `Some("alive")` for heartbeat events. A `.tmp` file created during atomic rename, or an editor swap file (`.001.json.swp`), is silently ignored — no test confirms this.
- **Proposed remediation:** Add a test that fires a synthetic `Event` with a `.json.tmp` path and confirms no panic, no output, and the previous-state map is unchanged.
- **Confidence:** medium

## F-089: `watch_with_receiver` seeds state from malformed status files silently
- **Severity:** low
- **Location:** `src/commands/watch.rs:125-138`
- **Description:** The seeding loop uses chained `.ok()` guards. A corrupt status file is skipped without warning, so the watcher starts up believing those tasks have no prior state — any subsequent status update appears as a first-seen transition.
- **Proposed remediation:** Log a warning to stderr for each file that fails to parse during seeding, and test with a mix of good + bad status files.
- **Confidence:** medium

## F-090: `worker::done::run_in` event emission / tmux-bell best-effort branch unasserted
- **Severity:** low
- **Location:** `src/commands/worker/done.rs:55-56`
- **Description:** `done::run_in` rings a tmux bell via `Tmux::new().signal_channel()` as best-effort (return value ignored). No test verifies the channel name format (`worker-{task_id}-done`) or that the failure is swallowed.
- **Proposed remediation:** Expose the channel-name builder as a pure helper (`fn done_channel_name(task_id: &str) -> String`) and unit test it; otherwise accept the gap.
- **Confidence:** low

## F-091: `worker::heartbeat::run` (the daemon loop) has no dedicated coverage
- **Severity:** low
- **Location:** `src/commands/worker/heartbeat.rs:11-18`
- **Description:** The testable unit `tick` is well covered. The `run` daemon loop — which calls `tick` then `thread::sleep(interval)` indefinitely — is untested. No exit path, no error propagation from repeated ticks, and no test of "if interval=0, behavior is sane".
- **Proposed remediation:** Refactor to extract the loop body and add a test that calls it once with a cancellation token, or accept this gap and document it with a `// Untested: daemon loop` comment.
- **Confidence:** medium

## F-092: `notes_file` growth is unbounded and unobserved
- **Severity:** low
- **Location:** `src/commands/worker/note.rs:29-36`
- **Description:** Notes are read in full, appended, and written back on every call. For a long-running task with hundreds of notes, each write is O(N). No test measures or caps file size, and there is no rotation. Combined with F-055 this makes pathological behavior possible in production.
- **Proposed remediation:** Switch to O(1) append (see F-055) and optionally implement rotation when file exceeds some threshold. Add a benchmark test.
- **Confidence:** low

## F-093: `worker::result::run_in` overwrites existing result file without warning
- **Severity:** low
- **Location:** `src/commands/worker/result.rs:21-43`
- **Description:** `std::fs::write(&result_file, &content)` truncates any pre-existing result. Tests cover "writes from file" and "fails if file not found" but not "overwrites existing result" or "writes empty string from stdin" (`stdin=true` with no input yields an empty buf; no test asserts that an empty result is accepted).
- **Proposed remediation:** Add a test that writes a result twice with different contents and asserts the second wins. Decide whether empty results should be rejected — add a test either way.
- **Confidence:** medium

## F-094: `events::emit` does not surface on missing run dir / read-only log parent
- **Severity:** low
- **Location:** `src/events.rs:11-27`
- **Description:** `emit` opens the log file with `create(true).append(true)`, wrapping the error with "failed to open events log: …". Paths not tested: (a) parent directory does not exist; (b) parent exists but is read-only; (c) log file exists but is a directory. Also `serde_json::to_string(&event)` — in practice this can't fail for a well-formed `OrcEvent`, but the error path has no test.
- **Proposed remediation:** Add `emit_returns_err_when_run_dir_missing` and `emit_returns_err_when_log_path_is_directory`.
- **Confidence:** medium

## F-095: `emit_warn` exercised but `Severity::Error` events have no emitter
- **Severity:** low
- **Location:** `src/events.rs:29-59`
- **Description:** `emit_info` and `emit_warn` are tested. There is no `emit_error` constructor and no event in the codebase is ever emitted with `Severity::Error` except a TUI mock in `src/tui/widgets/events.rs:122`. Either add the constructor + a failure path that uses it, or accept this as informational.
- **Proposed remediation:** Optional — add `emit_error` and wire it into the test-failure and merge-conflict branches of `integrate_in` (replacing `emit_warn` for severity-elevated events) then assert with `events::tail`.
- **Confidence:** medium

## F-096: `RunPaths::scaffold` leaves partial state on mid-failure
- **Severity:** low
- **Location:** `src/fs/run.rs:107-121`
- **Description:** The `for dir in &dirs` loop bails on the first `create_dir_all` error, leaving previously-created sibling dirs on disk. There is no cleanup or transactional rollback. No test injects a failure (e.g. a pre-existing file named `tasks` blocking creation of `tasks/`).
- **Proposed remediation:** Add a test that creates `runs/test-run/tasks` as a FILE, then calls `scaffold()`, and asserts the error message includes the path and that no other subdirs were created — OR document that partial scaffolds are acceptable.
- **Confidence:** low

## F-097: `frontmatter::upsert_field` error path for missing delimiters is untested
- **Severity:** low
- **Location:** `src/fs/frontmatter.rs:115-144`
- **Description:** `upsert_field` calls `split_frontmatter(content)?`. If `content` has no frontmatter at all, it returns an error, but no test covers this — only `update_field` tests exist. When the field is appended rather than replaced, the resulting YAML has no trailing newline before the closing `---` if the original yaml_str did not — this edge case is not asserted.
- **Proposed remediation:** Add tests: (1) upsert into plain markdown → `Err`, (2) upsert new key into single-line frontmatter → result parses round-trip cleanly.
- **Confidence:** medium

## F-098: `frontmatter::get_field` doesn't disambiguate absent vs. empty value
- **Severity:** low
- **Location:** `src/fs/frontmatter.rs:147-164`
- **Description:** A field present with no value returns `Ok(Some("".to_string()))`, while an absent field returns `Ok(None)`. `amend::replace_brief` iterates `SYSTEM_FIELDS` and uses `Ok(Some(v))` — so an empty value is preserved as `""`, which when upserted becomes `pane_id: ""` (quoted). No test confirms this round-trip.
- **Proposed remediation:** Decide on the semantics (treat empty as absent? preserve as-is?) and write a test pinning the behavior.
- **Confidence:** medium

## F-099: `RunMetadata.archived` flag never read, never written with a non-default value
- **Severity:** low
- **Location:** `src/model/run.rs:10`
- **Description:** The `archived` field exists with `#[serde(default)]` but no code path sets it to `true`, and `commands::run::archive_in` currently just removes the active symlink — it does not update archived metadata. Tests only assert `run_metadata_generates_id_from_slug` and filesystem-safe sanitization. Latent dead state or an incomplete feature.
- **Proposed remediation:** Either wire `archive_in` to persist `archived = true` into a run-level metadata file (currently `run.rs` defines `RunMetadata` but nothing writes it to disk), or delete the field. If kept, add `archive_in_marks_run_as_archived`.
- **Confidence:** high

## F-100: `RunMetadata::new` missing edge-case tests for empty/unicode/long slugs
- **Severity:** low
- **Location:** `src/model/run.rs:13-32`
- **Description:** Two tests cover `RunMetadata::new`. Uncovered: (a) empty string slug (produces `id = "<timestamp>-"` — is that valid or a bug?); (b) unicode slug (e.g. `"日本語-test"`) — the sanitizer replaces all non-ASCII with `-` so the id becomes a run of dashes, which might collide; (c) a 1000-char slug — no length cap means filenames could exceed filesystem limits (`NAME_MAX = 255` on Linux); (d) `archived` field default deserialization from old JSON.
- **Proposed remediation:** Add `run_metadata_empty_slug`, `run_metadata_unicode_slug_collapses_to_dashes`, `run_metadata_respects_max_filesystem_name_length`, `run_metadata_backward_compat_without_archived`.
- **Confidence:** medium

## F-101: `model::worker::PaneId` unused and untested
- **Severity:** low
- **Location:** `src/model/worker.rs:1-11`
- **Description:** `PaneId(String)` is defined with `Display` + `Serialize`/`Deserialize` + `PartialEq`/`Eq`, but `TaskStatus.pane_id` is typed as `Option<String>` (not `Option<PaneId>`) and no test references `PaneId`. This is either a premature newtype or dead code. A roundtrip test and a `Display` test are trivial if kept.
- **Proposed remediation:** Either adopt `PaneId` in `TaskStatus` + `TaskBriefFrontmatter` (behind a serde-transparent wrapper) and add `pane_id_display_roundtrip` + `pane_id_roundtrips_through_json`, or delete `PaneId`.
- **Confidence:** high

## F-102: Several tmux static-arg builders are untested
- **Severity:** low
- **Location:** `src/tmux/wrapper.rs:110-119, 162-186, 188-201`
- **Description:** `tests/tmux_test.rs` covers most `build_*_args` functions but not `build_list_panes_with_titles_args`. Additionally, `split_right` and `split_below` do not expose a `build_*_args` function and therefore have *no* testable entry point — their argv is assembled inline (`&format!("{percentage}%")`). A user passing `percentage = 0` or `percentage > 100` would produce `"0%"` / `"150%"` with no guard.
- **Proposed remediation:** Add `tmux_build_list_panes_with_titles_args` test mirroring existing builders. Extract `build_split_right_args(percentage: u32) -> Vec<String>` and `build_split_below_args(target_pane: &str, percentage: u32) -> Vec<String>`, test with boundary values (0, 50, 100, 150), and consider adding a `debug_assert!(percentage <= 100)` or clamping.
- **Confidence:** high

## F-103: `AnimState::tick` rate-limiter boundary untested; `shimmer_phase` accumulation untested
- **Severity:** low
- **Location:** `src/tui/anim/mod.rs:40-70`
- **Description:** The inline tests `tick_advances_angle` and `tick_disabled_does_not_advance` cover the enabled/disabled boolean but not the 100ms rate-limiter (lines 46-48) or `shimmer_phase` accumulation at different `activity_level`s (lines 54-59 — four-branch match untested). `activity_level = u32::MAX` — does the `match` fall through correctly to the `_ => 1.8` arm?
- **Proposed remediation:** Add `tick_rate_limited_under_100ms_is_noop`, `tick_shimmer_speed_by_activity_level` (for levels 0, 1, 3, 5), `tick_activity_level_max_uses_fastest_shimmer`.
- **Confidence:** high

## F-104: Anim widget: `render_info`, `render_shimmer`, `lerp_u8` untested
- **Severity:** low
- **Location:** `src/tui/anim/widget.rs:37-146, 158-195`
- **Description:** The inline tests only cover `depth_to_style` and `render_donut` with zero area. `render_info` contains significant logic: info-line truncation, dot-leader width calc, three-line brand block centering, horizontal centering via char-count-not-byte-count (explicitly flagged as unicode-correctness-sensitive). `render_shimmer`'s gaussian brightness wave and `lerp_u8` channel-mixing are entirely untested; a typo like `.pow(2)` vs `* dist` would ship silently.
- **Proposed remediation:** Add `lerp_u8_boundaries` (t=0 → a, t=1 → b), `lerp_u8_mid` (t=0.5 → avg), `render_info_narrow_area_clips_safely`, `render_info_centers_unicode_banner_by_chars`, `render_shimmer_returns_lighter_color_at_peak`.
- **Confidence:** medium

## F-105: `anim::render::draw_line_dotted` never exercised
- **Severity:** low
- **Location:** `src/tui/anim/render.rs:242-275`
- **Description:** `draw_line_dotted` is invoked on line 55 for very-far-back edges (`avg_depth > 0.8`). The inline tests in `render.rs` exercise `draw_line` but not the dotted variant. Untested: (a) that it writes `·` glyphs; (b) that it skips every other step (`.step_by(2)`); (c) the `slot.is_none()` guard — dotted draws should *not* overwrite existing cells; (d) zero-length dotted line returns without panic.
- **Proposed remediation:** Add `draw_line_dotted_uses_dot_glyph`, `draw_line_dotted_skips_every_other_step`, `draw_line_dotted_does_not_overwrite`, `draw_line_dotted_zero_length_no_panic`.
- **Confidence:** high

## F-106: `App::refresh` does not respect stale-heartbeat load errors; no test for error-path fallback
- **Severity:** low
- **Location:** `src/tui/app.rs:100-139`
- **Description:** `refresh` uses `.unwrap_or_default()` three times (lines 101, 104, 132) to swallow all errors from `collect_statuses`, `find_stale_heartbeats`, and `events::tail`. This is load-bearing behavior (TUI must not crash when reloading) but no test verifies: (a) if `statuses.json` becomes corrupt, refresh keeps the dashboard alive with an empty `statuses` vec; (b) the `selected` clamp on lines 127-129; (c) `active_count()` feeding `anim.activity_level`.
- **Proposed remediation:** Add `app_refresh_with_corrupt_status_file_survives`, `app_refresh_clamps_selection_when_statuses_shrink`, `app_refresh_updates_anim_activity_from_active_count`.
- **Confidence:** high

## F-107: Test fixtures leak credentials-shaped strings and don't pass `--local` to `git config`
- **Severity:** low
- **Location:** `tests/common/mod.rs:19-20`
- **Description:** `init_test_repo` writes `user.email = "test@test.com"` and `user.name = "Test"` into per-repo git config. Harmless today, but some security-scanner pre-commit hooks flag fixed email patterns. The git config is written after `git init` without the `--local` flag — if the test were ever run with `GIT_CONFIG_GLOBAL` pointing at a real user home, it could accidentally overwrite the developer's global config. Current behaviour defaults to `--local`, so this is low-severity.
- **Proposed remediation:** Pass `--local` explicitly to the two `git config` invocations. Consider also passing `commit.gpgsign=false` to avoid hook-triggered signing prompts on developers with global `commit.gpgsign=true`.
- **Confidence:** medium

## F-108: `classify_*` tests in `audit_test.rs` are pure-function tests in an integration binary
- **Severity:** low
- **Location:** `tests/audit_test.rs:200-267`
- **Description:** The `classify_test_file`, `classify_test_file_nested`, `classify_impl_file`, `classify_impl_file_nested`, `classify_mixed_commit` tests exercise the pure `classify_commit(files: &[String]) -> CommitKind` function — no TempDir, no git. They could live as unit tests in `src/audit.rs` where `classify_commit` is defined. Keeping them in the integration-test binary means a classification bug requires rebuilding and linking the entire test binary.
- **Proposed remediation:** Move the five `classify_*` tests into `#[cfg(test)] mod tests` inside `src/audit.rs`. Leave the `audit_with_test_commits`, `audit_no_tests`, `audit_empty_branch`, `audit_with_mixed_commits` integration tests where they are.
- **Confidence:** high

## F-109: `dashboard_test::mouse_event_variant_exists` is a compile-time check dressed as a runtime test
- **Severity:** low
- **Location:** `tests/dashboard_test.rs:115-131`
- **Description:** The test constructs an `Event::Mouse(MouseEvent{…})` and asserts `matches!(event, Event::Mouse(_))`. This is tautological — the match arm is guaranteed to succeed at compile time. The only thing this proves is that `Event::Mouse` is public and has the documented shape, which is a compile-time property. No runtime behaviour is verified.
- **Proposed remediation:** Delete the test, or replace it with a test that drives the App through `app.handle_event(Event::Mouse(…))` and asserts the App state changes as expected.
- **Confidence:** high

## F-110: `detect_test.rs::parse_tokens_k_format` missing edge cases
- **Severity:** low
- **Location:** `tests/detect_test.rs:64-91`
- **Description:** `parse_tokens_k_format` asserts `"1.7k" → 1700`, `"24.5k" → 24500`, `"1.2M" → 1200000`. No tests cover: empty suffix with decimal (`"1.7"`), exponent overflow (`"999.9M"`), negative (`"−1k"`), locale variants (`"1,7k"` German decimal separator). No tests cover the boundary between "k" and "M" (`"999k"` vs `"1.0M"`).
- **Proposed remediation:** Add edge-case tests for empty string, whitespace-only, very large values, trailing punctuation, mid-sentence matches, and multiple token mentions in one capture.
- **Confidence:** medium

## F-111: `parse_tokens_from_text` tests don't verify `None` consistently across edge cases
- **Severity:** low
- **Location:** `tests/detect_test.rs:88-91`
- **Description:** `parse_tokens_none_when_absent` asserts `None` for a string with no token pattern. It does not assert `None` (or specific value) for: `"↓ tokens"` (no number), `"↓ 0 tokens"` (should be `Some(0)`?), `"↓ .5k tokens"` (leading decimal), `"↓ 1k"` (missing "tokens" suffix).
- **Proposed remediation:** Add boundary tests for "0 tokens", missing suffix, leading decimal, negative, and NaN-like input. Document the function's contract in a rustdoc comment, then add tests that match the doc.
- **Confidence:** medium

## F-112: Large `integrate_test` setup helpers write repeated task-brief strings that should be data-driven
- **Severity:** low
- **Location:** `tests/integrate_test.rs:36-46, 88-96, 161-170`
- **Description:** Three setup helpers each contain the same pair of `format!("---\nid: \"{}\"\n...")` brief templates, differing only in slug and branch suffix. ~60 lines of boilerplate that could collapse to 2 lines using a `writer_brief` helper (see F-073). Maintenance debt, not a correctness bug.
- **Proposed remediation:** Same as F-073 — add `common::writer_brief` and `common::seed_writer_worktree(tmp, paths, id, slug, base, file_changes)`.
- **Confidence:** high

## F-113: `validate_duplicate_ids_returns_error` has ambiguous coverage (filename-prefix vs. frontmatter-id)
- **Severity:** low
- **Location:** `tests/plan_test.rs:80-96, 21-33`
- **Description:** `write_brief(tasks_dir, "001", "first", &[])` writes `001-first.md`. Then `write_brief(tasks_dir, "001", "duplicate", &[])` writes `001-duplicate.md`. Two files on disk, both with `id: "001"` in frontmatter. If the production code were rewritten to detect duplicates only by filename prefix (`001-*.md`), this test would still pass because the filenames also collide.
- **Proposed remediation:** Add a second test that writes `001-first.md` with `id: "001"` and `002-first.md` with `id: "001"` (filenames differ, frontmatter ids collide) — this unambiguously exercises frontmatter-based duplicate detection.
- **Confidence:** medium

## F-114: `resume_fails_with_no_active_run` and a dozen peers assert `is_err()` without checking the error type
- **Severity:** low
- **Location:** `tests/resume_test.rs:68-74`, `tests/fault_injection.rs:110-112`, `tests/amend_test.rs:236-247`, `tests/teardown_test.rs:38-41`, `tests/run_test.rs:60-63`
- **Description:** `assert!(result.is_err())` with no further check accepts *any* error — a malformed frontmatter, a panicking thread, a `NotInitialized` error, or the actually-intended `NoActiveRun` error. If a future refactor causes `format_resume` to bail earlier with `NotInitialized` before the NoActiveRun check, these tests still pass while the production message changes. Some tests do check the error message; many don't. Particularly bad: `tests/fault_injection.rs:110-112` — `fault_resume_no_active_run` only does `assert!(result.is_err())`.
- **Proposed remediation:** For every `assert!(result.is_err())` in the tree, either match the specific `AppError` variant (`matches!(err, AppError::NoActiveRun)`) or assert a stable substring of the error message. The project already defines typed errors in `src/model/error.rs` — use them.
- **Confidence:** high

## F-115: No test for clean teardown when filesystem failures occur
- **Severity:** low
- **Location:** `tests/teardown_test.rs` (whole file)
- **Description:** Standard happy-path tests exist for teardown, but there is no fault-injection test for filesystem-level failure (read-only worktree directory, missing worktree directory, locked git index). Integrate tests cover merge conflicts, but teardown's failure modes (common in practice — stale `.git/worktrees/` lock files after a crashed worker) are untested.
- **Proposed remediation:** Add a test that makes `worktree_dir("001")` read-only via `std::fs::set_permissions(…, Permissions::from_mode(0o555))` and asserts `teardown_task` returns a specific error type. Add a test that creates a dangling `.git/worktrees/001` lock file and asserts `teardown_task` recovers or errors cleanly.
- **Confidence:** medium

## F-116: `worker_note_appends_with_timestamp` asserts `"202"` as proof of timestamp presence
- **Severity:** low
- **Location:** `tests/worker_commands_test.rs:83-94`
- **Description:** `assert!(notes.contains("202"));` proves a timestamp starting with "202" is present — presumably "2026-…". This assertion will silently rot on 2030-01-01 and must be updated. More importantly, if the note format changes from ISO-8601 to anything else, the `"202"` substring might still appear coincidentally. Low severity because the subsequent `matches("[20").count()` assertion is more robust.
- **Proposed remediation:** Replace `notes.contains("202")` with a regex match on ISO-8601-like pattern or a hand-rolled check for `notes.contains("-04-") && notes.contains("T")`. Even better: have `note::run_in` return the timestamp, and assert on that directly.
- **Confidence:** medium

## F-117: `OrcEvent::Severity::Error` never emitted in production code
- **Severity:** low
- **Location:** `src/events.rs:29-59` (emitters); `src/tui/widgets/events.rs:122` (only use site)
- **Description:** Every `emit_*` helper produces `Severity::Info` or `Severity::Warn`. The `Severity::Error` variant exists in the model and is rendered by the TUI with a distinctive color, but nothing in the codebase emits one. Either the variant is aspirational (then tests should document the intent) or severity elevation is missing from `integrate::run_tests_with_output` and `audit_tdd` failure paths.
- **Proposed remediation:** Decide the contract. If `Error` is reserved for unrecoverable errors (e.g. `reset_hard_head` failure in F-016), add an `emit_error` helper and wire it at the appropriate sites, then assert via `events::tail`. Otherwise remove the variant.
- **Confidence:** medium

## F-118: TaskBrief frontmatter schema has no version field and no roundtrip test to defend against schema drift
- **Severity:** low
- **Location:** `src/model/task.rs` (schema), `tests/fs_test.rs` (partial coverage)
- **Description:** `TaskBriefFrontmatter` is parsed from YAML via serde, but there is no `schema_version` field and no test asserting backward compatibility when new optional fields are added. The `#[serde(default)]` pattern used in `OrchestratorConfig` (see F-062) is absent here. As `amend::replace_brief` preserves system fields, any future addition of a new system field requires a migration plan that is not tested.
- **Proposed remediation:** Add a `schema_version: Option<u8>` field defaulting to 1; add a backward-compat test that deserializes a pinned-on-disk sample brief from a prior schema.
- **Confidence:** medium

---

## Appendix: specialist finding coverage

| Specialist | File | Findings | Severities |
|---|---|---|---|
| qa-expert (coverage matrix) | /tmp/audit-001-qa-expert-coverage.md | 28 | 4C / 8H / 9M / 7L |
| test-automator (commands + fs) | /tmp/audit-001-test-automator-cmdfs.md | 40 | 2C / 8H / 19M / 11L |
| test-automator (tui/events/audit/tmux/model) | /tmp/audit-001-test-automator-tui.md | 26 | 1C / 3H / 11M / 11L |
| qa-expert (test quality/flake/isolation) | /tmp/audit-001-qa-expert-quality.md | 30 | 3C / 9H / 9M / 9L |
| **raw total** | | **124** | **10C / 28H / 48M / 38L** |
| **consolidated** (6 cross-specialist duplicates merged) | | **118** | **10C / 27H / 41M / 40L** |

Consolidations applied:
- F-002 = coverage F-04 + cmdfs F-05 (checkpoint::restore_in)
- F-012 = coverage F-05 + cmdfs F-06 (checkpoint::list_in)
- F-011 = coverage F-07 + tui F-25 (audit_tdd TddViolation emission)
- F-064 = coverage F-21 + tui F-16 (TaskState::can_transition_to matrix)
- F-101 = coverage F-28 + tui F-15 (PaneId dead code)
- F-057 = coverage F-20 + tui F-10 + tui F-11 (detect_from_text keyword gaps + Display/icon)

F-087 is a placeholder so downstream numbering stays stable across the three commit-heavy spawn findings (F-006/F-047/F-048/F-049).

## Cross-cutting themes worth phase-2 attention

1. **No atomic writes on the file-based event bus.** `fs/bus.rs`, `worker/note.rs`, `worker/status.rs`, `worker/heartbeat.rs`, `spawn.rs` all read-modify-write without locks or tempfile+rename. F-048, F-049, F-054, F-055 should move as a unit.
2. **Panics on `task.branch.unwrap()` across `integrate.rs`.** F-003, F-004 are independent but share the same root cause (schema-level Option unwrapped); consider a type-state refactor (`WriterBrief` newtype where `branch` is non-Option by construction).
3. **`tests/common/mod.rs` is the bottleneck.** F-009, F-010, F-029, F-030, F-073, F-107, F-112 all reduce to "extend common with real helpers and delete duplicates."
4. **Weak `assert!(result.is_err())` pattern is endemic.** F-114 enumerates five files; fix touches `fault_injection.rs`, `resume_test.rs`, `amend_test.rs`, `teardown_test.rs`, `run_test.rs`.
5. **Exhaustive enum round-trips** (`EventType`, `Severity`, `TaskState`, `DetectedState`, `AppError` Display) — F-007, F-057, F-063, F-064, F-066 — all fixable with a single table-driven test file.
6. **Dead or partially-wired features**: `SortOrder::cycle_sort` (F-027), `PaneId` (F-101), `RunMetadata.archived` (F-099), `Severity::Error` (F-117), `AppError::{BranchExists, DirtyBaseBranch, TmuxError, GitError, InvalidStateTransition, TestFailure}` (F-007). Phase 2 should decide per-item: wire-in, delete, or `#[allow(dead_code)]` with tracking issue.
