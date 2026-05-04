---
domain: rust-impl
task_id: "006"
auditors:
  - voltagent-lang:rust-engineer (24 findings: 2 critical / 8 high / 10 medium / 4 low)
  - voltagent-qa-sec:architect-reviewer (22 findings: 2 critical / 5 high / 10 medium / 5 low)
totals:
  total: 44
  critical: 4
  high: 13
  medium: 18
  low: 9
---

# Phase 1 Audit — rust-impl

## Summary

agentrc is a disciplined Rust 2021 codebase: no `unsafe` anywhere, zero-panic compilation
under rustc stable, consistent use of `?` for error propagation, and clean top-level
separation between `model/`, `fs/`, `git/`, `tmux/`, `detect/`, `commands/`, and `tui/`.
Layering is mostly respected — low-level infrastructure never depends on high-level
orchestration.

The serious issues cluster into five themes. (1) **Two user-reachable panics** — a
`panic!` in both `integrate_in` and `dry_run_in` when a writer task brief lacks a
`branch` field (src/commands/integrate.rs:193, :274), and load-bearing `HashMap::get_mut().unwrap()`
calls inside `detect_cycle`/`topo_sort` that will silently break under future refactors
(src/commands/plan.rs). (2) **Two inverted-layer dependencies** — `commands/status.rs`
imports a presentation helper from `tui/widgets/table.rs`, and six sibling command modules
reach into `commands::spawn` purely to access `load_task_brief`/`find_task_brief`, making
`spawn` the de facto task-brief library. (3) **Aspirational error type** — ~half of
`AppError`'s variants (`TmuxError`, `GitError`, `DirtyBaseBranch`, `BranchExists`,
`MergeConflict`, `TestFailure`, `NotInitialized`, `InvalidStateTransition`) are declared
but never constructed; callers fall back to `anyhow::bail!("…")` strings, losing the typed
variant. (4) **File bloat** — `src/commands/integrate.rs` (524 lines fusing CLI + git +
diagnostics), `src/commands/spawn.rs::run` (140-line function with 9 responsibilities),
`src/main.rs` (295 lines of clap definitions that belong in `src/cli.rs`), and
`src/tui/anim/render.rs` (498 lines mixing transform/raster/glyph concerns). (5)
**Dependency hygiene** — `duct = "0.13"` is entirely unused; `serde_yaml = "0.9"` is
archived upstream and will be flagged by `cargo audit`.

Secondary themes worth addressing: triple-mapped `TaskState` string representations that
only the compiler catches two of, seven-way duplication of `load_config` boilerplate,
`state_symbol`/`state_color`/`is_graveyard` duplicated between `commands::status` and
`tui::widgets::table` (with glyphs already diverged), a hard-coded `"workers"` tmux window
name in five places, and `tests/common/mod.rs` containing only `init_test_repo` while 20+
tests duplicate the active-run + frontmatter fixture setup. Nothing here blocks shipping,
but the coupling-to-`spawn` and config-loading duplication materially obstruct
refactoring, and the two `panic!` sites are real crash risks in the hottest orchestration
path.

---

## F-01: `panic!` inside integrate on missing writer branch
- **Severity:** critical
- **Location:** `src/commands/integrate.rs:193-197` and `src/commands/integrate.rs:274-278`
- **Description:** `dry_run_in` and `integrate_in` both iterate over writer tasks and do `let branch = task.branch.as_deref().unwrap_or_else(|| panic!("writer task {} has no branch", task.id));`. A writer brief without a `branch` field is user-reachable (handwritten briefs, YAML where the field was omitted or renamed) and the call chain reaches these functions from both the CLI (`agentrc integrate`) and the dashboard action (`'i'` key binding in `src/tui/action.rs:81`). The panic would crash the orchestrator at the point where the user most needs it to keep running — mid-integration, possibly after some branches have already merged.
- **Proposed remediation:** Validate in `collect_writer_tasks_ordered` that every writer has a branch, skip (with a warning) or return `AppError::TaskBriefParseError` for those that don't. The `MergeResult` could also gain a "missing-branch" variant, but the cheapest fix is to filter them out before reaching the hot loop.
- **Confidence:** high

## F-02: `.unwrap()` on `HashMap::get_mut` inside library DAG code
- **Severity:** critical
- **Location:** `src/commands/plan.rs:160`, `src/commands/plan.rs:162-163`, `src/commands/plan.rs:182`, `src/commands/plan.rs:222`
- **Description:** `detect_cycle` keeps an `in_degree: HashMap<&str, usize>` and `dependents: HashMap<&str, Vec<&str>>` keyed on `brief.id.as_str()`. Inside the main loops it does `*in_degree.get_mut(brief.id.as_str()).unwrap() += 1;` and `dependents.get_mut(dep.as_str()).unwrap().push(...)`, and later `brief.depends_on.iter().find(...).unwrap()`. The invariant that the key was inserted at the top of the function is load-bearing — any code refactor that narrows the keyset will silently introduce a panic. The final `.unwrap()` at line 222 depends on the in-degree filter keeping at least one node in the cycle with a dependency edge into the cycle; if the graph is corrupt (e.g. a dep string that *wasn't* in `id_set` somehow slips through because of a future change), this panics. Library code used by both `plan validate` and `integrate` should not have these.
- **Proposed remediation:** Either use `in_degree.entry(id).or_insert(0)` / `*entry += 1` which is the idiomatic form, or return `Option<String>` and bail out early if the invariants break. For the `.find().unwrap()` at line 222, guard with `if let Some(next) = ... else { break; }`.
- **Confidence:** high

## F-03: `commands::spawn` has become the task-brief library — 6 non-spawn callers reach into its internals
- **Severity:** critical
- **Location:** `src/commands/spawn.rs:20` (`load_task_brief`), `src/commands/spawn.rs:33` (`find_task_brief`). Consumers: `src/audit.rs:5`, `src/commands/respawn.rs:5`, `src/commands/plan.rs:5`, `src/commands/integrate.rs:8`, `src/commands/amend.rs:5`, `src/commands/checkpoint.rs:7`.
- **Description:** Six modules (`audit`, `respawn`, `plan`, `integrate`, `amend`, `checkpoint`) depend on the `spawn` command module solely to parse/locate task briefs. This is a classic sibling-coupling anti-pattern: `spawn` is ostensibly one CLI subcommand peer to the others, yet every peer links into it. It also means any refactor of `spawn.rs` (e.g. splitting into `spawn_tmux.rs` + `spawn_worktree.rs` — see F-11) risks breaking every other command. `load_task_brief` is just YAML frontmatter parsing of a file; it has nothing to do with spawning.
- **Proposed remediation:** Create `src/fs/task_brief.rs` (or promote into `src/model/task.rs`) with `pub fn load(path: &Path) -> Result<TaskBriefFrontmatter>` and `pub fn find(run: &RunPaths, task_id: &str) -> Result<PathBuf>`. Delete the two `pub fn`s from `commands/spawn.rs` and update imports in the 6 dependents. `spawn` then depends on `fs::task_brief`, which is the correct direction.
- **Confidence:** high

## F-04: `src/commands/status.rs` imports from `src/tui/widgets/` — presentation layer leak into CLI layer
- **Severity:** critical
- **Location:** `src/commands/status.rs:11` (`use crate::tui::widgets::table::format_tokens;`)
- **Description:** `commands/status.rs` is the non-TUI CLI status renderer (emits ANSI escapes to stdout). It reaches into `tui::widgets::table` — a ratatui-specific widget module — to borrow `format_tokens`. The direction is wrong: `commands/` is a lower-level orchestrator surface and `tui/` is a higher-level presentation. This pins the CLI command to ratatui's widget hierarchy and makes it impossible to strip ratatui without touching `status.rs`. It also signals that `format_tokens` is actually a model/util helper, not a widget helper.
- **Proposed remediation:** Move `format_tokens` out of `src/tui/widgets/table.rs` into a neutral location (e.g. a new `src/model/format.rs` or `src/fmt.rs`, or `src/commands/status.rs` itself and re-export to tui). Have both `src/commands/status.rs:11` and `src/tui/widgets/header.rs:6` import from the new location. No behaviour change; purely a home move.
- **Confidence:** high

---

## F-05: `serde_yaml = "0.9"` is deprecated (archived upstream)
- **Severity:** high
- **Location:** `Cargo.toml:16`
- **Description:** `dtolnay/serde-yaml` was archived by the author in 2024 and marked unmaintained; `cargo audit` / RUSTSEC will flag it. It is used in `src/fs/frontmatter.rs:44` and in two tests for parsing YAML frontmatter. Since the actual parse needs are trivial (flat key: value frontmatter) this is a replaceable dep.
- **Proposed remediation:** Switch to `serde_yaml_ng` (a maintained fork with the same API) or `serde_yml`. Alternatively, given the narrow usage (typed frontmatter via `serde::Deserialize`), consider parsing by hand: `frontmatter.rs` is already doing line-oriented manipulation in `update_field`/`upsert_field`/`get_field` without serde, so the crate is only needed for the typed `parse<T>` path used by `TaskBriefFrontmatter`. Either replacement or a minimal in-tree YAML-subset parser is viable.
- **Confidence:** high

## F-06: `duct` dependency is entirely unused
- **Severity:** high
- **Location:** `Cargo.toml:19`
- **Description:** `duct = "0.13"` is declared but `rg 'duct::|use duct|duct!'` returns zero hits in `src/` or `tests/`. The only references are in the design doc at `docs/agentrc-phase1-plan.md`. Both `src/tmux/wrapper.rs` and `src/git/wrapper.rs` build their own `Command::new("…").args(…).output()` helpers. This adds ~20 transitive crates to the build for zero value.
- **Proposed remediation:** Remove `duct = "0.13"` from `Cargo.toml`. If the long-term intent is to adopt it, file an issue; otherwise keep the hand-rolled `Command` helpers.
- **Confidence:** high

## F-07: `load_config(paths)` boilerplate is duplicated verbatim across 8 command modules
- **Severity:** high
- **Location:** `src/tui/app.rs:47-53`, `src/commands/respawn.rs:29-33` & `:182-188`, `src/commands/checkpoint.rs:59-65`, `src/commands/resume.rs:34-43`, `src/commands/amend.rs:39-46`, `src/commands/layout.rs:97-108`, `src/commands/integrate.rs:423-436`, `src/commands/spawn.rs:113-117`
- **Description:** Eight sites read `.orchestrator/config.json` with nearly identical patterns (`paths.config()` → `read_to_string` → `serde_json::from_str`), differing only in whether they fall back to `OrchestratorConfig::default()` on missing file, and whether they propagate errors via `?` or `with_context`. This is a clear missing abstraction on `OrchestratorPaths` or `OrchestratorConfig`. Any schema change or snapshot-vs-project-config rule change requires editing 8 call sites (as `integrate.rs:423-436` already demonstrates with its run-snapshot-preferred variant).
- **Proposed remediation:** Add `impl OrchestratorConfig { pub fn load(paths: &OrchestratorPaths) -> Result<Self>; pub fn load_or_default(paths: &OrchestratorPaths) -> Result<Self>; pub fn load_preferring_snapshot(paths: &OrchestratorPaths, run: &RunPaths) -> Result<Self>; }` in `src/model/config.rs`. Replace the 8 call sites. `integrate.rs::load_config` becomes a one-liner delegation.
- **Confidence:** high

## F-08: `unreachable!()` in amend path that the CLI layer does not fully guard
- **Severity:** high
- **Location:** `src/commands/amend.rs:76-78`
- **Description:** `run_in` has `let updated_content = if let Some(...) = brief_path { ... } else if let Some(msg) = message { ... } else { unreachable!() };`. This is supposed to be unreachable because of the `AmendSourceRequired` check at line 28, but if a future refactor moves that check, the error becomes a `panic!` instead of a typed error. In a library entry point (`run_in` is called by `main.rs:233` directly and could also be called by tests or future callers) this is fragile.
- **Proposed remediation:** Combine into a single `match` on `(brief_path, message)` that has a single `(None, None) => return Err(AppError::AmendSourceRequired.into())` arm, so the types make the invariant visible to the compiler rather than the programmer.
- **Confidence:** high

## F-09: Silent error discard via `.ok()` loses context on status JSON parse
- **Severity:** high
- **Location:** `src/commands/watch.rs:22-23`, `src/commands/checkpoint.rs:76`, `src/commands/checkpoint.rs:169`, `src/commands/checkpoint.rs:210`
- **Description:** In `watch.rs` `process_status_change` does `.ok()?` on both `read_to_string` and `serde_json::from_str`, silently suppressing any parse errors for a status file — a corrupted `.json` just goes unnoticed, which defeats the purpose of a dashboard-like watcher. In `checkpoint.rs:76` the fallback chain `find_task_brief(&active, &status.id).ok().and_then(|p| load_task_brief(&p).ok())` loses two different error contexts (brief-not-found vs. brief-parse-failed), so the checkpoint silently records `slug: "unknown"`.
- **Proposed remediation:** In `watch.rs::process_status_change`, change return type to `Result<Option<String>>` and let the caller log errors while continuing. In `checkpoint.rs`, preserve the error via `.map_err` + `eprintln!` so at least a warning is emitted. `events.rs::tail` at `:77` is a similar pattern but more defensible because the comment explicitly documents "skip unparseable lines (e.g. truncated writes from crashes)" — that one is fine.
- **Confidence:** high

## F-10: `src/commands/integrate.rs` is 524 lines and fuses CLI printing, orchestration, git I/O, test execution, and diagnostics
- **Severity:** high
- **Location:** `src/commands/integrate.rs:1-524`
- **Description:** Single file contains: (1) five public structs (`MergeResult`, `DryRunEntry`, `FileOverlap`, `DryRunReport`, plus internal `TestOutput`); (2) CLI output formatting (`run` lines 63-125, `run_dry_run` 128-163); (3) the top-level `integrate_in` state machine (241-416); (4) `dry_run_in` (173-226); (5) private helpers `load_config`, `collect_writer_tasks_ordered`, `run_tests_with_output`, `truncate_lines`, `append_log`. The body of `integrate_in` is a 175-line `for task in &tasks` loop with nested `match` arms that inline event emission, log writing, result struct construction, and rollback — no step is individually testable and comprehension requires reading the full loop.
- **Proposed remediation:** Split along the natural seams: (a) `src/commands/integrate/mod.rs` — CLI entry `run`, `run_dry_run`, print helpers; (b) `src/commands/integrate/plan.rs` — `DryRunEntry`, `DryRunReport`, `dry_run_in`, `collect_writer_tasks_ordered`, `load_config`; (c) `src/commands/integrate/engine.rs` — `MergeResult`, `integrate_in`, the per-task loop refactored into `fn try_merge_one(git, task, config, ...) -> MergeResult`; (d) `src/commands/integrate/diagnostics.rs` — `run_tests_with_output`, `truncate_lines`, `append_log`. `integrate_in` becomes a 30-line driver calling `try_merge_one` per task.
- **Confidence:** high

## F-11: `src/commands/spawn.rs::run` does 9 responsibilities including tmux orchestration; pure helpers are intermingled
- **Severity:** high
- **Location:** `src/commands/spawn.rs:103-242` (the 140-line `pub fn run`)
- **Description:** The `run` function sequentially: parses a brief, loads config, enforces `max_workers`, creates a worktree, writes initial status, creates/splits a tmux window, sets a pane title, patches the brief frontmatter with `pane_id`, patches the status JSON with `pane_id`/`pane_title`, retiles, sends 4 `send_keys` commands (export, cd, heartbeat, claude launch), and emits an event. The numbered comments (1…9, with 6 missing, two labelled 9) show the author already thinks of it as staged but the stages are glued together by shared local variables rather than function boundaries. Pure helpers (`load_task_brief`, `find_task_brief`, `setup_worktree`, `write_initial_status`, `generate_seed_prompt`) sit above `run` as separate `pub fn`s that tests actually use, but they form only steps 1–4 and the rest is inline.
- **Proposed remediation:** Extract three more testable helpers: `fn ensure_under_max_workers(cwd, config) -> Result<()>` (lines 119–139), `fn acquire_worker_pane(tmux, window_name) -> Result<String>` (lines 158–170), and `fn launch_worker_in_pane(tmux, pane_id, cwd, work_dir, claude_cmd) -> Result<()>` (lines 196–232). The main `run` becomes a 40-line driver. Move `fn run` and the helpers that only serve `run` (e.g. status patching) into a submodule if desired, but the primary win is giving each side-effecting stage its own name.
- **Confidence:** high

## F-12: `state_symbol`, `state_color`, and `is_graveyard` duplicated between `commands::status` and `tui::widgets::table`
- **Severity:** high
- **Location:** `src/commands/status.rs:25-47` vs `src/tui/widgets/table.rs:20-41,71-76`; also `src/tui/action.rs:11-16` has a third `is_graveyard` copy
- **Description:** `state_symbol(&TaskState) -> &'static str` exists twice with near-identical bodies (different symbols for `Ready`: `○` in both, but tui uses `◌`/`◇` for spawning/ready and status uses `◌`/`○` — the spawning glyph now diverges between CLI and TUI). `state_color` exists twice with different return types (`String` of ANSI vs `ratatui::Color`) but same RGB triples. `is_graveyard` is defined three times. When a `TaskState` variant is added, all three files must be updated in lock-step.
- **Proposed remediation:** Add inherent methods on `TaskState` in `src/model/task.rs`: `pub fn symbol(&self) -> char`, `pub fn is_graveyard(&self) -> bool`, and a single `pub fn rgb(&self) -> (u8,u8,u8)`. Both renderers convert via their own adapter (`Color::Rgb(r,g,b)` / `format!("\x1b[38;2;{r};{g};{b}m")`). Delete the six duplicate definitions.
- **Confidence:** high

## F-13: `format!("{key}:")` is recomputed on every line inside hot parse loops
- **Severity:** high
- **Location:** `src/fs/frontmatter.rs:65`, `:125`, `:152`, `:153`, `:155`
- **Description:** `update_field`, `upsert_field`, and `get_field` all build `format!("{key}:")` and `format!("{key} :")` prefixes *inside* the line-iteration closure/loop — i.e. once per line in the YAML. For small frontmatters the cost is negligible, but it's also an idiomaticity smell that makes the hot path less readable. The same `format!` calls at `:153` and `:155` are even used as arguments to `strip_prefix`, which means the format call happens whether or not the `starts_with` succeeded.
- **Proposed remediation:** Compute `let k1 = format!("{key}:"); let k2 = format!("{key} :");` once before the loop, then compare against those. This also makes the three near-duplicate blocks easier to refactor into a single helper `fn find_key_line<'a>(yaml: &'a str, key: &str) -> Option<(&'a str, &'a str)>` returning `(line, trimmed_rest)` so the update/upsert/get can share logic.
- **Confidence:** high

## F-14: `src/main.rs` holds 294 lines of clap definitions and a 72-line command-dispatch match — should live in `src/cli.rs`
- **Severity:** high
- **Location:** `src/main.rs:1-294`
- **Description:** The binary's `main.rs` contains the `Cli` struct, 4 subcommand enums (`Commands`, `PlanCommands`, `RunCommands`, `CheckpointCommands`, `WorkerCommands`), the `LayoutMode` enum, and a 72-line `match cli.command { … }` block that dispatches to `commands::*`. When adding a new subcommand you must touch a 300-line file; the clap structs also could not be consumed by tests/bench without pulling in the binary. `tests/cli_smoke_test.rs` uses `assert_cmd` to shell out to the binary because the clap structs aren't reachable from the lib.
- **Proposed remediation:** Move everything except `fn main` into a new `src/cli.rs` inside the library (`pub mod cli;` in `lib.rs`), exposing `pub struct Cli`, subcommand enums, and `pub fn dispatch(cli: Cli) -> Result<()>` that contains the big match. `main.rs` shrinks to `fn main() -> Result<()> { agentrc::cli::dispatch(agentrc::cli::Cli::parse()) }`. Subcommand parsing becomes unit-testable. Consider further splitting the 4 subcommand enums into `src/cli/worker.rs`, `src/cli/run.rs`, etc. if growth continues.
- **Confidence:** high

## F-15: `.unwrap()` in `main.rs` on `current_dir`
- **Severity:** high
- **Location:** `src/main.rs:232`
- **Description:** `let cwd = std::env::current_dir().expect("cannot determine current directory");` — every other top-level `main.rs` dispatch call goes through a function that calls `current_dir().context(…)?`. Only the `Amend` arm at line 227-234 calls `current_dir()` directly at the binary entry and uses `.expect()`. This is inconsistent, and under a weird env (deleted cwd inherited from parent, restricted container) will panic rather than return an error to the shell.
- **Proposed remediation:** Push the `std::env::current_dir()` call inside `commands::amend::run` (add a thin `pub fn run(task_id, brief, message) -> Result<()>` wrapper matching the other commands), so `main.rs` only calls `commands::amend::run(...)`.
- **Confidence:** high

## F-16: `AppError` has ~8 variants that are never constructed in production code
- **Severity:** high
- **Location:** `src/model/error.rs` — unused variants: `ConfigNotFound` (line 7), `InvalidStateTransition` (line 19), `DirtyBaseBranch` (line 28), `BranchExists` (line 34), `TmuxError` (line 37), `GitError` (line 40), `MergeConflict` (line 46), `TestFailure` (line 49), `NotInitialized` (line 52)
- **Description:** Nearly half of `AppError`'s 15 variants are aspirational — they correspond to conditions that in practice bubble up as `anyhow::bail!("…")` strings or `git`/`tmux` wrapper errors converted via `?`. Grep confirms these names appear only in the definition and in `tests/model_test.rs` tests that simply construct+display them, giving a false signal of use. `MergeConflict { task_id, files }` is especially misleading: `commands::integrate.rs:399` instead builds `message: format!("merge conflict on branch '{branch}'")` and stores structured conflict data in `MergeResult.conflicting_files` — the variant lies about the actual error channel. Meanwhile `src/commands/teardown.rs:112`, `src/commands/worker/status.rs:120`, `src/commands/amend.rs:55` use `anyhow::bail!("cannot tear down task ... state ...")`, `anyhow::bail!("invalid task state: {other}")`, `anyhow::bail!("no status file for task {task_id}")`, losing the machine-readable variant.
- **Proposed remediation:** Either (a) wire up the existing variants at the ~10 obvious call sites (`teardown.rs:112` -> `InvalidStateTransition`, `worker/status.rs:120` -> `InvalidStateTransition`, `amend.rs:55` -> `TaskNotFound`, `tmux::wrapper::run_tmux` -> `AppError::TmuxError`, `git::wrapper::run_git` -> `AppError::GitError`), or (b) delete the dead variants. Option (a) also means callers can `downcast_ref::<AppError>()` to branch on specific failures rather than stringifying. For variants reserved for planned features, mark the enum `#[non_exhaustive]` and keep a single "future use" sentinel rather than 8 placeholders.
- **Confidence:** high

## F-17: Unnecessary `format!("{x}")` on already-Display values
- **Severity:** high
- **Location:** `src/tui/widgets/table.rs:106` and `src/tui/widgets/table.rs:132`
- **Description:** `format!("{}", s.state)` (line 106) and `format!("{detected}"), Style::default()...` (line 132) are the format-string equivalent of `.to_string()` on a `Display` value. Clippy's `useless_format` lint flags these.
- **Proposed remediation:** Replace `format!("{x}")` with `x.to_string()`; clippy `useless_format` will flag them automatically.
- **Confidence:** high

---

## F-18: `.to_string()` on already-`String` values, awkward `format! + trim_matches + to_string` chain for EventType
- **Severity:** medium
- **Location:** `src/commands/events.rs:17-21`
- **Description:** `let etype = serde_json::to_string(&event.event_type).unwrap_or_default().trim_matches('"').to_string();` — this serialises the enum variant (which is `rename_all = "snake_case"`), stripping the JSON quotes. It's correct but (a) allocates twice (the `to_string` then the `trim_matches` gives a `&str`, then `.to_string()` reallocates) and (b) bypasses `Display` which would be the idiomatic way. The enum could have `#[derive(serde::Serialize)] + impl Display` via `strum` or a manual match; there's already a manual `Display` for `TaskState` so the pattern exists in-repo. (Also note a second label map in `src/tui/widgets/events.rs:8` duplicates the snake_case strings — consider unifying.)
- **Proposed remediation:** Implement `Display for EventType` with the same snake_case strings. Then this becomes `let etype = event.event_type.to_string();`.
- **Confidence:** high

## F-19: `.clone()` on `String` values that are only used to build short-lived structs
- **Severity:** medium
- **Location:** `src/commands/integrate.rs:205-213`, `src/commands/integrate.rs:263`, `src/commands/integrate.rs:373`, `src/commands/plan.rs:269`
- **Description:** In `dry_run_in`, `.push(task.id.clone())` inside `file_to_tasks.entry(f.clone()).or_default()` repeats a clone per (file, task) pair. Since `tasks` is owned locally and is later consumed only for a `DryRunEntry { task_id: task.id.clone(), branch: ..., changed_files }` that re-clones, the whole routine could iterate once with `into_iter()` and move `task.id` into the last use, and keep `&str` borrows inside the map. Similar in `integrate_in` — `task_changed_files.insert(task.id.clone(), files)`. For N=20 tasks this is trivial cost but the clones make the intent unclear.
- **Proposed remediation:** Change `file_to_tasks: HashMap<&str, Vec<&str>>` keyed on borrows and only allocate when constructing `FileOverlap` at the end. Or accept the clones — this is stylistic.
- **Confidence:** medium

## F-20: `filter(|...| ... == &task.id)` borrow-of-borrow comparison
- **Severity:** medium
- **Location:** `src/commands/integrate.rs:371`
- **Description:** `.filter(|(id, _)| *id != &task.id)` — the closure receives `&(&String, &Vec<String>)`, `id` binds to `&&String`, and `*id != &task.id` compares `&String != &String`, which works but is unusual. The idiom is `|(id, _)| id.as_str() != task.id.as_str()` or `|(id, _)| *id != &task.id` with `HashMap<String, ..>` changed to `HashMap<&str, ..>`.
- **Proposed remediation:** Change the key type to `&str` at the `task_changed_files` declaration (line 257) so the double-reference disappears and the filter reads cleanly.
- **Confidence:** medium

## F-21: `topo_sort` has quadratic `emitted.contains(&dep)` and `ids.contains(&dep)`
- **Severity:** medium
- **Location:** `src/commands/plan.rs:239-275`
- **Description:** `topo_sort` iterates remaining tasks inside a loop, and for each one calls `task.depends_on.iter().all(|dep| emitted.contains(dep) || !ids.contains(dep))`. Both `emitted` and `ids` are `Vec<String>` (lines 240 and 246), so each `.contains` is O(n). For N tasks with D average deps, total cost is O(N^3) in the worst case, plus each `emitted.push(task.id.clone())` clones a `String`. This function already has an implementation in `detect_cycle` that correctly uses `HashSet<&str>` and `HashMap` — the second impl (`topo_sort`) did not get the same treatment.
- **Proposed remediation:** Store `emitted` and `ids` as `HashSet<&str>` (or `HashSet<String>` if lifetimes are painful), and drop the `.clone()` on line 269. N is typically <20 so the performance is not the concern — the idiomaticity is.
- **Confidence:** high

## F-22: `.unwrap_or_default()` on `tmux.list_windows()` hides tmux-not-running errors
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:161`, `src/commands/respawn.rs:67`
- **Description:** `let windows = tmux.list_windows().unwrap_or_default();` — if tmux isn't running or the session is gone, we silently treat it as "no windows exist" and then call `tmux.new_window_with_pane_id(window_name)` which *will* fail, producing a confusing downstream error. The ancestor of these calls (`spawn::run`) already checks `max_workers` and sets up worktrees; by the time we fail it's partial state.
- **Proposed remediation:** Propagate the error with `?` and add a clearer message: `tmux.list_windows().context("tmux session not available — start tmux first")?`. The downside is that `spawn` now requires a running tmux, but that was already implicitly true.
- **Confidence:** medium

## F-23: `as u32` / `as u16` truncating casts without `checked_*`
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:131` `.count() as u32`, `src/commands/respawn.rs:192-193` `.map(|c| c.len() as u32)`, `src/commands/checkpoint.rs:99` `.map(|c| c.len() as u32)`, `src/tui/app.rs:138` `self.active_count() as u32`, `src/tui/app.rs:227-228` `.. as u16`
- **Description:** `usize -> u32` and `usize -> u16` casts with `as` silently truncate. For task counts and commits-ahead the values will always be small, but the idiomatic form is `u32::try_from(n).unwrap_or(u32::MAX)` or an explicit `n.min(u32::MAX as usize) as u32`. This is the kind of thing clippy-pedantic flags under `cast_possible_truncation`.
- **Proposed remediation:** Replace with `u32::try_from(n).unwrap_or(u32::MAX)` at the call sites. The TUI click handler (`app.rs:227-228`) is self-bounded by `terminal_height` (a `u16` already) so the cast is actually safe there, but adding a `try_into().unwrap_or(0)` documents intent.
- **Confidence:** medium

## F-24: `.to_string_lossy().to_string()` allocates twice
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:42`, `src/commands/run.rs:61`, `:97`, `:106`
- **Description:** `entry.file_name().to_string_lossy().to_string()` — `to_string_lossy` already returns `Cow<'_, str>` which is cheap in the common UTF-8 case; `.to_string()` then forces a copy into a fresh `String`. If the ultimate consumer is `String`, `into_owned()` is the idiomatic final step (it's a no-op when the `Cow` is already `Owned`).
- **Proposed remediation:** `entry.file_name().to_string_lossy().into_owned()`. Minor, but clippy `unnecessary_to_owned` catches it.
- **Confidence:** high

## F-25: `Result<bool>` for `branch_exists` hides semantics
- **Severity:** medium
- **Location:** `src/git/wrapper.rs:97-103`
- **Description:** `branch_exists` has signature `fn branch_exists(&self, branch: &str) -> Result<bool>` but it unconditionally returns `Ok(true|false)` (it maps `Err` into `Ok(false)`). This collapses "branch doesn't exist" with "git command failed for other reasons" (no git repo, permission error, out of disk). Every caller (`spawn.rs`, `checkpoint.rs:94`, `respawn.rs:177`) then does `.unwrap_or(false)` which is a no-op since the `Result` never holds an `Err`. So the `Result<bool>` return is effectively a `bool` masquerading as fallible.
- **Proposed remediation:** Either (a) return `bool` directly if the error-swallowing is intentional, or (b) use `Result<bool>` and remove the internal `Err(_) => Ok(false)`, letting real errors propagate. Option (b) is more idiomatic; callers that want "treat failure as not exist" would then need `.unwrap_or(false)` explicitly.
- **Confidence:** high

## F-26: `src/model/worker.rs::PaneId` is defined but has zero consumers — dead module
- **Severity:** medium
- **Location:** `src/model/worker.rs:1-11` (whole file)
- **Description:** `pub struct PaneId(pub String)` and its `Display` impl exist but are never imported, constructed, or referenced anywhere in `src/`, `tests/`, or `docs/` (only appears as a design-doc aspiration in `docs/agentrc-phase1-plan.md`). Pane IDs are passed as plain `String`/`&str` throughout (e.g. `TaskStatus::pane_id: Option<String>` at `src/model/task.rs:68`). The `worker.rs` module itself is listed in `src/model/mod.rs:6` but never contributes.
- **Proposed remediation:** Either delete `src/model/worker.rs` and its `pub mod worker;` line in `model/mod.rs`, or commit to `PaneId` as a newtype and replace `Option<String>` in `TaskStatus`, tmux wrapper signatures, etc. Given the ergonomic cost of adopting a newtype at this point, deletion is the pragmatic choice.
- **Confidence:** high

## F-27: `Tmux::build_*_args` duplicates every `run_tmux` instance call and allocates needlessly
- **Severity:** medium
- **Location:** `src/tmux/wrapper.rs:25-130` (11 `pub fn build_*_args` returning `Vec<String>`), consumed only in `tests/tmux_test.rs:5-102`
- **Description:** Every instance method (`split_window`, `send_keys`, `kill_pane`, etc.) is paired with a static `build_*_args` that returns the command-line tokens as `vec!["split-window".to_string(), "-h".to_string(), ...]` with hard-coded `.to_string()` on every literal. The tests then assert on those tokens, but the instance methods at lines 164-172, 177-185, etc., inline the *same* arg list a second time — so the abstraction is duplicated rather than reused. `send_keys` (line 204) can diverge from `build_send_keys_args` (line 38) with no compile-time guarantee. Several `build_*` (e.g. `build_list_panes_with_titles_args` at line 111) are not even asserted in `tmux_test.rs`. The overall shape is an awkward halfway-house between "testable arg builder" and "allocation-heavy wrapper".
- **Proposed remediation:** Refactor each instance method to be implemented in terms of its `build_*_args` counterpart: `pub fn send_keys(&self, pane_id, keys) -> Result<()> { self.run_with_args(&Self::build_send_keys_args(pane_id, keys)) }`. Then `build_*_args` is exercised by every integration path and the tests are meaningful. Also consider switching to `&[&str]` signatures (like `run_tmux(&self, args: &[&str])` at line 142-159 already does) so callers don't pay for the allocation, or `["split-window", "-h", ...].map(String::from)`. Alternatively, delete the duplicated `build_*_args` methods that have no test coverage and let instance methods inline the literals.
- **Confidence:** high

## F-28: `Tmux::split_right`, `split_below`, `wait_for_channel` are public but never called
- **Severity:** medium
- **Location:** `src/tmux/wrapper.rs:176` (`split_right`), `src/tmux/wrapper.rs:189` (`split_below`), `src/tmux/wrapper.rs:318` (`wait_for_channel`). Grep confirms no callers anywhere (including tests).
- **Description:** Three public methods with zero in-tree consumers. `split_right`/`split_below` appear designed for a dashboard layout split (20/80 columns) that was never wired, and `wait_for_channel` is the orchestrator-side counterpart to `signal_channel` (which *is* used by `worker/done.rs:56`) — but the orchestrator never blocks on worker signals.
- **Proposed remediation:** Delete them unless there's a near-term plan. Each is a 10-line method, so the cost of re-adding them when needed is trivial. If `wait_for_channel` is infrastructure for a future "wait-for-completion" dashboard feature, add a TODO comment with a filed issue ID; otherwise remove.
- **Confidence:** high

## F-29: The `"workers"` tmux window name is a hard-coded string literal duplicated in 5 places
- **Severity:** medium
- **Location:** `src/commands/spawn.rs:160`, `src/commands/respawn.rs:66`, `src/commands/layout.rs:45`, `src/commands/layout.rs:89`, `src/commands/layout.rs:117`
- **Description:** Five sites hardcode `"workers"` (and `"workers-"` prefix). If the convention changes (e.g. to include run id), all five must be updated together. This is exactly the kind of coupling that `OrchestratorPaths` avoided for the filesystem layout but that was never done for tmux window naming.
- **Proposed remediation:** Add `pub const WORKERS_WINDOW_PREFIX: &str = "workers";` (plus a helper `pub fn is_workers_window(name: &str) -> bool { name == WORKERS_WINDOW_PREFIX || name.starts_with("workers-") }`) in `src/tmux/mod.rs`. Update the 5 sites.
- **Confidence:** high

## F-30: `src/tui/anim/render.rs` is 498 lines doing 3D math, shape selection, rasterisation, and glyph mapping
- **Severity:** medium
- **Location:** `src/tui/anim/render.rs:1-498`
- **Description:** The file contains `render_frame` (dispatches by `Shape`), rotation math (`rotate_vertex`, `project`), line drawing (`draw_line`, `draw_line_dotted`), glyph selection (`vertex_char`, `edge_char`, `torus_brightness_char`), and all their tests. 292 lines of code + 206 lines of tests. It shares concerns with `shapes.rs` (geometry) but owns both the 3D transform pipeline and the 2D rasterisation — two classic separable concerns. The resulting file is dense and hard to navigate.
- **Proposed remediation:** Split into `src/tui/anim/transform.rs` (rotate_vertex, project, tests for them), `src/tui/anim/raster.rs` (AnimCell, draw_line, draw_line_dotted), `src/tui/anim/glyphs.rs` (vertex_char, edge_char, torus_brightness_char). `render.rs` keeps `render_frame` and orchestrates the three. Pure refactor, ~100 line files each.
- **Confidence:** medium

## F-31: `.iter()` on fixed-size arrays where 2021-edition `IntoIterator` works
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:200-201`, `src/tui/anim/shapes.rs:164`, `src/commands/install.rs:36`
- **Description:** Rust 2021 made `IntoIterator for [T; N]` yield `T` by value, so `["ID","STATE",...].iter().map(|h| Cell::from(*h)...)` can be `["ID",...].into_iter().map(|h| Cell::from(h)...)` dropping the `*h`. `[v.0, v.1, v.2].iter().filter(|c| c.abs() > 1e-10).count()` in `shapes.rs:164` can be `[v.0, v.1, v.2].into_iter().filter(|c| c.abs() > 1e-10).count()` (works because `f64: Copy`). `install.rs:36` `for cmd in &["claude", "tmux", "git"]` is fine but `for cmd in ["claude", "tmux", "git"]` is more 2021-native.
- **Proposed remediation:** Mechanical switch to `.into_iter()` / direct iteration where the element type is `Copy`. Clippy's `into_iter_on_ref` lint will flag the affected sites.
- **Confidence:** medium

## F-32: `App::sort_order` is tracked and cycled but never read — dead UI state
- **Severity:** medium
- **Location:** `src/tui/app.rs:30` (field), `src/tui/app.rs:161-167` (`cycle_sort`), `src/commands/dashboard.rs:58` (`'s' => app.cycle_sort()`). Grep for reads: `.sort_order` is assigned but never read (no match for `app.sort_order |` as condition anywhere).
- **Description:** The `s` key cycles `sort_order` through `Id → State → Elapsed`, but no render path or `refresh` applies the sort — `refresh` calls `collect_statuses` which sorts by id unconditionally (`src/commands/status.rs:89`). The help overlay advertises this key ("Cycle sort order"), so users get no feedback when pressing `s`. Either a feature drop or incomplete feature.
- **Proposed remediation:** Either (a) wire it up: at the end of `App::refresh`, call `self.statuses.sort_by(match self.sort_order { … })`; or (b) remove `SortOrder`, the field, `cycle_sort`, the 's' key handler in `dashboard.rs`, and the help entry in `widgets/help.rs`. Pick one in a single commit.
- **Confidence:** high

## F-33: `src/tui/app.rs::App::new` constructor does I/O, tmux scans, and struct assembly in one 50-line block
- **Severity:** medium
- **Location:** `src/tui/app.rs:45-98`, plus the `#[cfg(test)] fn test_app` escape hatch at 260-281
- **Description:** `App::new` reads config, resolves active run id, probes `$TMUX_PANE`, calls `tmux list_panes_with_titles`, then builds a 16-field `App` struct. Because of the I/O, tests cannot use `App::new` on a bare path — they need `fn test_app` (lines 260-281) which duplicates the 16-field initialiser. Another duplicate 16-field initialiser exists in `src/tui/widgets/events.rs:167-186` (in a unit test). The `App::new` failure modes (no active run) are silently mapped to `run_id = "none"` rather than surfaced.
- **Proposed remediation:** Split `App::new` into `App::from_config(config: OrchestratorConfig, project_root: PathBuf, run_id: String, orchestrator_pane: Option<String>) -> App` (pure struct construction) and `App::load(project_root: PathBuf) -> Result<App>` (does the I/O and calls `from_config`). Delete the two 16-field test constructors in favour of `App::from_config(Default::default(), …)`. Also supplies a `Default for App` for tests.
- **Confidence:** medium

## F-34: `src/tui/widgets/table.rs` is 329 lines and its row-builder takes 7 flat parameters
- **Severity:** medium
- **Location:** `src/tui/widgets/table.rs:78-197` (`build_row` with `(s, detected, max_tokens, now, graveyard, stale) -> Row<'static>`), plus near-identical `render_workers`/`render_graveyard` duplicate functions (221-273 vs 276-328)
- **Description:** `render_workers` and `render_graveyard` are 54-line twins differing only in a filter and a title/style — copy-paste bug territory. `build_row` takes a flat tuple of rendering hints and mutates its behaviour by the `graveyard`/`stale` booleans, which is a common sign that the row builder should dispatch on a `RowStyle` enum or should just be called with a pre-computed `Style`. `WIDTHS` is a module-level `const`.
- **Proposed remediation:** Introduce `fn render_table(app, area, buf, title: &str, filter: impl Fn(&TaskStatus) -> bool, highlight_bg: Color)` and call it from two 4-line wrappers. Replace `build_row`'s boolean params with a `RowMode { Active { stale: bool }, Graveyard }` enum. Net line reduction ~80.
- **Confidence:** medium

## F-35: `tests/common/mod.rs` holds only `init_test_repo` while 20+ test files duplicate fixture setup
- **Severity:** medium
- **Location:** `tests/common/mod.rs:1-25` (only `init_test_repo` helper). Duplicated setups in `tests/spawn_test.rs:8-30`, `tests/amend_test.rs:9-40`, `tests/respawn_test.rs:9-40`, `tests/audit_test.rs:14-86` (private `git()` + `setup_audit_test_repo` + `create_branch_with_commits`), `tests/integrate_test.rs:9-55` (`setup_two_writer_tasks`), `tests/happy_path.rs` (frontmatter format! templates repeated 4×), `tests/events_test.rs:11-19` (`setup_active_run`).
- **Description:** 17 tests call `init_test_repo`, and 16 tests then call `init::run_in + run::create_in` in sequence. The `format!("---\nid: \"{}\"\nslug: {}\nclassification: writer\n…")` frontmatter template is repeated ~9 times across `happy_path.rs`/`integrate_test.rs`/`fault_injection.rs`. `tests/audit_test.rs:14-28` defines a private `fn git()` that replays `init_test_repo`'s internal helper. `tests/events_test.rs:11-19` and `tests/audit_test.rs:42-48` both hand-craft the `.orchestrator/active -> runs/test-run` symlink.
- **Proposed remediation:** Expand `tests/common/mod.rs` with `pub fn init_with_active_run(tmp: &TempDir, slug: &str) -> (OrchestratorPaths, RunPaths, String /*base_branch*/)`, `pub fn write_writer_brief(active: &RunPaths, id: &str, slug: &str, base: &str)`, `pub fn git(repo: &Path, args: &[&str])`, and `pub fn run_git_in_worktree(wt: &Path, args: &[&str])`. Refactor the 20+ test files. Net line reduction in tests should be ~400 lines.
- **Confidence:** high

---

## F-36: `src/audit.rs` lives at the crate root while `src/commands/audit.rs` is its CLI wrapper — asymmetric with `events`
- **Severity:** low
- **Location:** `src/audit.rs` (91 lines: `classify_commit`, `audit_tdd`, `TddAudit`, `CommitKind`), `src/commands/audit.rs` (21 lines: thin CLI adapter). Same pattern for `src/events.rs` / `src/commands/events.rs`.
- **Description:** Both `audit.rs` and `events.rs` are top-level single-file modules providing domain logic that a CLI wrapper in `src/commands/` delegates to. That's a valid pattern, but `audit.rs` is inconsistently placed: its logic is closer in nature to `src/commands/` (it reads `run` metadata, calls git, emits events) than to the infrastructure modules (`fs`, `git`, `tmux`). Meanwhile the domain types `TddAudit`, `CommitKind` would arguably belong in `src/model/`.
- **Proposed remediation:** Option A (minimal): move `src/audit.rs` → `src/commands/audit/engine.rs` so it sits alongside its CLI wrapper. Option B (cleaner): split into `src/model/audit.rs` (the `TddAudit`, `CommitKind` data types) and `src/commands/audit.rs` (engine + CLI). Same treatment for `events.rs` — the `emit`/`tail` functions are I/O utilities that could live in `src/fs/events.rs` next to `fs/bus.rs`.
- **Confidence:** medium

## F-37: Pure-logic `CommitKind` / `classify_commit` leaks to `pub` but is only used by tests
- **Severity:** low
- **Location:** `src/audit.rs:12-29` (`pub enum CommitKind`, `pub fn classify_commit`)
- **Description:** `classify_commit` and `CommitKind` are marked `pub`, but the only external consumer is `tests/audit_test.rs` which imports them via `use agentrc::audit::{audit_tdd, classify_commit, CommitKind};`. Within `src/`, `classify_commit` is called only once, from `audit_tdd` (line 66). So the `pub` is driven entirely by testability. This is a fair use of `pub`, but it signals that the module boundary hasn't been thought through — `CommitKind` is really an impl detail, and tests could exercise `classify_commit` through `audit_tdd` on a constructed repo.
- **Proposed remediation:** Mark `CommitKind` and `classify_commit` as `pub(crate)` and move the 8 `classify_*` unit tests in `tests/audit_test.rs:200-268` into a `#[cfg(test)] mod tests` block inside `src/audit.rs`. This reduces the public API surface. Alternatively, keep `pub` and document it with `/// Exposed for test harnesses…`.
- **Confidence:** medium

## F-38: `Result<Option<T>, E>` return in `frontmatter::get_field` is reasonable but `.ok()` downstream loses the parse error
- **Severity:** low
- **Location:** `src/fs/frontmatter.rs:147-164`, `src/commands/amend.rs:113`
- **Description:** `get_field(content, key) -> Result<Option<String>>` is idiomatic (`Err` = malformed frontmatter, `Ok(None)` = key absent). But the only caller in `amend.rs:113` does `if let Ok(Some(value)) = frontmatter::get_field(original_content, field) { ... }` — this collapses "malformed frontmatter" into "field absent" silently, which can cause the amend to drop previously-set system fields like `pane_id` if the YAML is slightly broken. The `Result` vs `Option` distinction exists but isn't being used.
- **Proposed remediation:** At `amend.rs:113`, propagate parse errors via `?`. If the frontmatter is unparseable we should fail loudly rather than lose `pane_id` / `worktree` / `created_at` during a replacement.
- **Confidence:** medium

## F-39: `new_window_with_pane_id` + `list_windows` flow can silently create a duplicate `workers` window
- **Severity:** low
- **Location:** `src/commands/spawn.rs:164-166`, `src/commands/respawn.rs:69`
- **Description:** The rest of `spawn::run` uses `tmux.new_window_with_pane_id(window_name).context("failed to create workers window")?` (correct). But the prior `tmux.list_windows().unwrap_or_default()` on line 161 then drives `if !windows.iter().any(|w| w == window_name)` — if tmux listing failed we treat the window as absent and create it, but then if a window of that name already existed we'd create a second `workers` window silently. Low severity because tmux allows duplicate window names, but the resulting behaviour (split into a fresh empty window) is surprising and not what the user wanted.
- **Proposed remediation:** Propagate the `list_windows()` error (see F-22). If we keep `unwrap_or_default`, log a warning on the error path.
- **Confidence:** medium

## F-40: `events::tail` builds full Vec then skips; could use `Iterator::rev + take`
- **Severity:** low
- **Location:** `src/events.rs:74-81`
- **Description:** Reads the whole file, `filter_map`s into `Vec<OrcEvent>`, then `skip(events.len().saturating_sub(count))` — allocating the whole vector even when the user asked for the last 20 events of a 10k-line log. Not a hot path but not great.
- **Proposed remediation:** `content.lines().rev().filter_map(|l| serde_json::from_str(l).ok()).take(count).collect::<Vec<_>>().into_iter().rev().collect()` — or use a `VecDeque` with a max size. Alternatively, seek to the file tail. Since events logs are bounded in size in practice this is low severity.
- **Confidence:** medium

## F-41: `TaskState` has three parallel string mappings; only two are compiler-checked
- **Severity:** low
- **Location:** `src/model/task.rs:44-56`, `src/commands/worker/status.rs:111-122`
- **Description:** `TaskState` has both a hand-rolled `Display` (matching snake_case) *and* `#[serde(rename_all = "snake_case")]`. Its `parse_state` in `worker/status.rs:111-122` is a third parallel mapping that hard-codes the same strings. If someone adds a variant, three places need updating and the compiler only flags two (the `match` in `Display` and the `match` in `parse_state`). `strum::{Display, EnumString, AsRefStr}` would derive all three from one source of truth.
- **Proposed remediation:** Either add a small `strum` dep and derive `Display + EnumString`, or collapse `parse_state` into `serde_json::from_str::<TaskState>(&format!("\"{s}\""))` which reuses the serde derive. The latter needs no new dep.
- **Confidence:** high

## F-42: Multi-pane scan orchestration lives in `App::refresh` instead of `detect/`
- **Severity:** low
- **Location:** `src/tui/app.rs:106-124` (per-task `scan_pane_full` loop + orchestrator-pane `capture_pane`), `src/detect/mod.rs:164-183` (`scan_pane` / `scan_pane_full`)
- **Description:** `detect/mod.rs` has single-pane scan helpers, but the *multi-pane* orchestration (iterate tasks, update detected map, separately scan orchestrator pane for tokens) lives inside `App::refresh`. This mixes dashboard state management with the "what does a running system look like" probe. It also makes CLI commands (e.g. `status`, which today doesn't use `DetectedState` at all) unable to reuse the aggregate scan.
- **Proposed remediation:** Add `pub fn scan_all_panes(tmux: &Tmux, tasks: &mut [TaskStatus]) -> HashMap<String, DetectedState>` to `src/detect/mod.rs`, encapsulating the loop at `src/tui/app.rs:108-117` and the token-usage backfill. `App::refresh` calls it as a one-liner. Enables reusing pane scanning from other commands (e.g. `status --detect`).
- **Confidence:** medium

## F-43: `src/tui/event.rs` spawns a thread that floods an unbounded channel with `Event::Tick`
- **Severity:** low
- **Location:** `src/tui/event.rs:14-46`
- **Description:** The thread loop at lines 22-42 polls crossterm with `tick_rate`, optionally sends a key/mouse event, and *then always* sends `Event::Tick` — which floods the receiver with ticks on every 100ms iteration, plus extra ticks when events fire. The dashboard (`commands/dashboard.rs:108`) only advances animation/refresh on ticks, so an over-eager tick doesn't cause bugs, but the channel backlog can grow during a stalled render and the animation speed is effectively unrelated to the requested `tick_rate`. The `mpsc` channel is unbounded. No structural bug, but a timing/resource concern.
- **Proposed remediation:** Change the loop to `if event::poll(tick_rate)? { dispatch event } else { tx.send(Event::Tick) }` so ticks fire only on idle. Alternatively keep the current structure but cap the channel with `sync_channel(16)` to drop backlog if the consumer falls behind.
- **Confidence:** medium

## F-44: `src/tui/widgets/events.rs::toggle_events_key` test duplicates the 16-field `App` struct literal and tests app state, not widget rendering
- **Severity:** low
- **Location:** `src/tui/widgets/events.rs:89-202` (tests), specifically `fn toggle_events_key` at 165-201 that builds a full `App` struct literal just to flip `show_events`
- **Description:** A widget rendering test for the events panel (`events_panel_renders` at 118-147) is fine and belongs here. But `toggle_events_key` (165-201) tests `App::show_events` toggling — not anything widget-related — and hand-builds a 16-field `App` literal, duplicating the `test_app` constructor in `src/tui/app.rs:260-281`. The test belongs next to `App` or in `tests/dashboard_test.rs`.
- **Proposed remediation:** Move `toggle_events_key` into `src/tui/app.rs::tests` and use the existing `fn test_app` helper. Keep only `events_panel_renders` and `events_panel_empty` in the widget module. Addresses the duplicate 16-field struct-literal issue flagged in F-33.
- **Confidence:** high
