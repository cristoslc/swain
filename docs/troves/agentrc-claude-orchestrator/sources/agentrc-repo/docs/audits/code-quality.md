---
domain: code-quality
task_id: "004"
totals:
  critical: 3
  high: 11
  medium: 13
  low: 10
  total: 37
created_at: 2026-04-12
---

# Phase 1 Audit — code-quality

## Summary

The `agent.rc` codebase (~12 kLOC Rust, 39 source files, 16 test files) is
small, consistent in tone, and uses `anyhow::Result` throughout the CLI/IO
layer with a `thiserror`-based `AppError` for semantic errors. It is,
however, carrying a well-defined cluster of duplication smells from rapid
iteration that an audit sweep should pay down together. The dominant issues
are (1) a production-reachable `panic!` in the `integrate` merge loop when
a writer brief has no branch frontmatter, (2) pervasive copy/paste of the
`current_dir → OrchestratorPaths::new → active_run()` prelude across 25+
command entry points, (3) the 524-LOC `commands/integrate.rs` mixing CLI
formatting, merge orchestration, topo-sort, test-runner, and log-append
into one file, (4) four subtly different `OrchestratorConfig` loaders
spread across seven sites with conflicting "missing → default" semantics,
(5) state-symbol/colour tables duplicated across CLI and TUI, and (6)
spawn/respawn sharing 70 lines of verbatim pane-bootstrap code. Beneath
the duplication layer are smaller hazards: a dead `TaskState` state-machine
guard, nine orphan `AppError` variants, `spawn::load_task_brief` being
imported by six downstream commands (wrong home), and `tui/app.rs`
reverse-engineering the layout in `tui/ui.rs` to do click-to-row mapping.

Clippy (pedantic) surfaces 361 warnings of which ~356 are duplicate
`uninlined_format_args` across test targets (mechanical fix, one pass);
the only non-test findings are one unused import and a handful of
pedantic-only float/time warnings inside test helpers. No critical
security or undefined-behaviour lints.

This report merges findings from a `code-reviewer` pass and a
`refactoring-specialist` pass, de-duplicated and re-ordered by severity
then file path. Findings F-01..F-03 are the critical items for Phase 2
remediation; F-04..F-14 are the high-leverage refactors that, done
together, remove ~200 LOC of boilerplate. F-15..F-27 are medium polish,
F-28..F-37 are low-risk cleanups.

Scope: `src/` and `tests/` trees. Excluded: `target/`.

---

## F-01: `integrate_in` and `dry_run_in` panic on a writer task with no branch

- **Severity:** critical
- **Location:** `src/commands/integrate.rs:194-197` and `src/commands/integrate.rs:275-278`
- **Description:** Both `dry_run_in` and `integrate_in` resolve each writer task's branch with `task.branch.as_deref().unwrap_or_else(|| panic!("writer task {} has no branch", task.id))`. `TaskBriefFrontmatter::branch` is `Option<String>` and is legitimately absent in several flows: `spawn::run` synthesises a default `orc/<id>-<slug>` branch at spawn time (so the brief on disk may lack one pre-spawn), and `respawn::validate_respawn` falls back to a synthesised name when both brief and status lack a branch. An operator running `agentrc integrate` on a plan whose writer brief has never been spawned, or whose brief was hand-edited to drop the `branch:` key, hits `panic!` instead of a clean `AppError`. Reachable with valid-looking input.
- **Proposed remediation:** Replace both `unwrap_or_else(|| panic!(...))` with a `?`-returning helper — `let branch = task.branch.as_deref().ok_or_else(|| anyhow!("writer task {} has no branch in frontmatter", task.id))?;`, or introduce a dedicated `AppError::TaskBriefMissingBranch { task_id }` variant and propagate. Apply the same pattern in both functions so they stay in lockstep.
- **Confidence:** high

## F-02: Command prelude duplication — extract a `CommandContext`

- **Severity:** critical
- **Location:** 25+ sites. Representative: `src/commands/spawn.rs:104-117`, `src/commands/respawn.rs:15-33`, `src/commands/checkpoint.rs:41-65`, `src/commands/teardown.rs:14-33`, `src/commands/watch.rs:66-73`, `src/commands/integrate.rs:64-175,241-247,422-436`, `src/commands/status.rs:51-66`, `src/commands/worker/*.rs`, `src/commands/plan.rs:25-42`, `src/commands/amend.rs:32-46`, `src/commands/resume.rs:24-43`, `src/audit.rs:42-44`, `src/events.rs:13,63`.
- **Description:** Nearly every CLI entry point opens with the same sequence: `std::env::current_dir().context("cannot determine current directory")?` → `OrchestratorPaths::new(&cwd)` → `paths.active_run().ok_or(AppError::NoActiveRun)?` → (for most) read `config.json` and parse `OrchestratorConfig`. That pattern is verbatim or near-verbatim in 20+ files. `audit.rs:6` and `events.rs:6` omit the `.context(...)` — itself an inconsistency. This is the single largest source of boilerplate in the crate, and the `NoActiveRun` guard is silently absent from any future command that forgets it. Changing the prelude (e.g. adding env-var overrides) requires touching all call sites.
- **Proposed remediation:** Introduce `src/commands/context.rs` with `pub struct CommandContext { pub project_root: PathBuf, pub paths: OrchestratorPaths, pub active: RunPaths, pub config: OrchestratorConfig }` exposing `from_cwd() -> Result<Self>` and `from_root(root: &Path) -> Result<Self>`. Every `run`/`run_in` opens with `let ctx = CommandContext::from_root(project_root)?;`. Pair with `impl OrchestratorPaths { fn load_config(&self) -> Result<OrchestratorConfig>; fn load_config_or_default(&self) -> OrchestratorConfig }` so F-05 collapses into this change.
- **Confidence:** high

## F-03: `commands/integrate.rs` packs five unrelated concerns into 524 LOC

- **Severity:** critical
- **Location:** `src/commands/integrate.rs:1-524`
- **Description:** The file holds (1) public result types (`MergeResult`, `DryRunEntry`, `FileOverlap`, `DryRunReport` at L17-60); (2) CLI output formatting with hand-tuned column widths (L77-122, L136-160); (3) the merge engine (`integrate_in` at L241-415, ~175 lines with three near-identical match arms that construct `MergeResult` literals and emit events); (4) the dry-run engine (`dry_run_in` at L173-226); (5) writer-task collection via directory walk + frontmatter re-parse (`collect_writer_tasks_ordered` at L441-477, duplicating the walk in `plan.rs`); (6) a shell-backed test runner (`TestOutput`, `run_tests_with_output`, `truncate_lines` at L479-512); (7) integration-log append helper (`append_log` at L515-523). The merge loop alone is where the drift risk concentrates.
- **Proposed remediation:** Convert to a `commands/integrate/` submodule: `mod.rs` (CLI `run`, `run_dry_run`), `types.rs` (result/report structs), `engine.rs` (`integrate_in`, `dry_run_in`), `tasks.rs` (`collect_writer_tasks_ordered`; pairs with F-22 moving `topo_sort` out of `plan.rs` into `model::graph`), `test_runner.rs` (`TestOutput`, `run_tests_with_output`, `truncate_lines`), `report.rs` (pretty-printing), `log.rs` (`append_log`). Dependency direction: `mod → report → engine → {types, tasks, test_runner, log}`. Expect net LOC reduction once F-07 and F-14 are applied.
- **Confidence:** high

## F-04: `tui/anim/render.rs` (498 LOC) mixes shape dispatch, 3D math, and 2D rasteriser

- **Severity:** high
- **Location:** `src/tui/anim/render.rs:1-498` (~200 LOC production + ~300 LOC tests)
- **Description:** Four distinct concerns packed in: (a) frame dispatcher `render_frame` (L19-111) with a nested `match state.shape` at L28-33 after the outer match; (b) 3D math primitives `rotate_vertex`, `project` (L113-159); (c) 2D rasteriser `draw_line`, `draw_line_dotted`, `edge_char` (L185-275) — shape-agnostic; (d) glyph pickers `vertex_char`, `torus_brightness_char` (L166-178, L280-292). The rasteriser is used only internally but bloats the module.
- **Proposed remediation:** Split into `src/tui/anim/render/{mod.rs, math.rs, raster.rs, wireframe.rs, torus.rs}`. `mod.rs` holds `AnimCell` and public `render_frame` as a three-arm dispatcher. `math.rs` holds `rotate_vertex`/`project`. `raster.rs` holds the line-drawing + `edge_char`. `wireframe.rs` consumes math+raster for cube/octahedron. `torus.rs` consumes math for the torus plus `torus_brightness_char`. Per-helper tests move with their helpers — each new file stays under 200 LOC. No public API change; `anim/mod.rs` re-exports `AnimCell` and `render_frame`.
- **Confidence:** high

## F-05: `OrchestratorConfig` loading diverges across 7 callers with 4 different "missing" behaviours

- **Severity:** high
- **Location:** `src/commands/integrate.rs:423-436` (snapshot-preferred, fail on missing), `src/commands/checkpoint.rs:59-65` (project-only, default on missing), `src/commands/amend.rs:39-46` (project-only, default on missing, with `.context`), `src/commands/respawn.rs:29-33` (project-only, bails with `?`), `src/commands/respawn.rs:181-188` (project-only, default on missing — SECOND call in the same module), `src/commands/resume.rs:34-43` (snapshot-only, fail on missing), `src/commands/spawn.rs:113-117` (project-only, bails), `src/commands/layout.rs:97-108` (project-only, default), `src/tui/app.rs:46-53`.
- **Description:** Eight call sites, four conflicting policies regarding "what to do on missing config" and "snapshot vs project". `respawn.rs` even loads the config twice in the same flow with different fallback behaviour (L29 errors, L183 defaults). The snapshot-preferred path is a real design invariant for `integrate`/`resume`, but nothing documents that invariant or prevents drift.
- **Proposed remediation:** Centralise on `OrchestratorConfig`: `impl OrchestratorConfig { pub fn load_project(paths: &OrchestratorPaths) -> Result<Self>; pub fn load_project_or_default(paths: &OrchestratorPaths) -> Self; pub fn load_run_snapshot(active: &RunPaths) -> Result<Self>; pub fn load_effective(paths: &OrchestratorPaths, active: &RunPaths) -> Result<Self>; }` — the last being "snapshot preferred, fall back to project". Document: `integrate`/`resume` → `load_effective`; pre-run commands → `load_project_or_default`. Folds into F-02's `CommandContext`.
- **Confidence:** high

## F-06: Worker-pane bootstrap duplicated verbatim between spawn and respawn

- **Severity:** high
- **Location:** `src/commands/spawn.rs:158-232` vs `src/commands/respawn.rs:65-107`
- **Description:** Both commands run the same 7-step dance: `list_windows()` → `new_window_with_pane_id("workers")`-or-`split_window("workers")` → `select_layout_tiled("workers")` → `set_pane_title` → send `export AGENTRC_PROJECT_ROOT=...` → send `cd <workdir>` → send `agentrc worker heartbeat ... &` → build+escape a `claude --dangerously-skip-permissions '…'` command with `worker_claude_args` → send it. The shell-escape `seed.replace('\'', "'\\''")` at `spawn.rs:226` and `respawn.rs:101` is byte-identical. The pane title `format!("orc:{id}:{slug}")` appears at `spawn.rs:173` and `respawn.rs:78`. Six separate `"workers"` string literals across `spawn.rs`, `respawn.rs`, `layout.rs`, `tui/anim/widget.rs`.
- **Proposed remediation:** Extract `src/commands/worker_pane.rs` with `pub struct PaneBootstrap<'a> { project_root, work_dir, task_id, pane_title, seed_prompt, heartbeat_interval_sec, worker_claude_args }` and `pub fn launch(tmux: &Tmux, cfg: &PaneBootstrap) -> Result<String>` returning the pane id. Both commands reduce to assembling a `PaneBootstrap` and calling `launch`. Hoist `const WORKER_WINDOW: &str = "workers";` to share across call sites. The `'`-escape and claude-command build live inside `launch` only.
- **Confidence:** high

## F-07: `MergeResult` is three disjoint result shapes fused via boolean flags

- **Severity:** high
- **Location:** `src/commands/integrate.rs:17-34`, construction at L321-333, L344-356, L392-404
- **Description:** `MergeResult` carries mutually-exclusive `success`/`conflict`/`test_failure` bools (the `run()` printer at L81-89 treats them as an enum), plus `conflicting_files` and `overlapping_tasks` that are populated only in the conflict arm, plus `touched_files` and `test_stderr` populated only in the test-failure arm. Every construction site sets `Vec::new()` / `None` for the irrelevant fields. This is textbook primitive-obsession and forces callers to consult three booleans to learn which fields are meaningful.
- **Proposed remediation:** Replace with a tagged enum: `pub struct MergeResult { task_id, branch, commit_history, outcome: MergeOutcome }` and `pub enum MergeOutcome { Merged, Conflict { files: Vec<String>, overlapping_tasks: Vec<String> }, TestFailure { touched_files: Vec<String>, stderr: Option<String> } }`. `run()`'s `if-else if-else` ladder collapses to one `match result.outcome`. Move the `message` string onto `impl MergeOutcome { fn describe(&self) -> &'static str }`. Combines well with F-14.
- **Confidence:** high

## F-08: `spawn::load_task_brief` / `find_task_brief` are the wrong home for a crate-wide helper

- **Severity:** high
- **Location:** `src/commands/spawn.rs:20-53` (definition); callers: `src/commands/plan.rs:5`, `src/commands/checkpoint.rs:7`, `src/commands/integrate.rs:8`, `src/commands/respawn.rs:5`, `src/commands/amend.rs:5`, `src/audit.rs:5`
- **Description:** The two most-used helpers in the codebase are exported from `commands::spawn`, so every command that touches a task brief depends on the spawn command module. This inverts the natural direction (plan validation should not transitively depend on the spawn CLI) and means any refactor of spawn's public surface risks breaking plan/checkpoint/integrate/respawn/amend/audit. There is no technical reason these helpers live in a CLI command module.
- **Proposed remediation:** Move to `src/fs/tasks.rs` (or extend `src/model/task.rs`): `pub fn load_brief(path: &Path) -> Result<TaskBriefFrontmatter>; pub fn find_brief(run: &RunPaths, task_id: &str) -> Result<PathBuf>; pub fn iter_briefs(run: &RunPaths) -> Result<impl Iterator<Item = Result<TaskBriefFrontmatter>>>`. The third folds in the directory-walk boilerplate currently in `plan::validate_in` L52-70 and `integrate::collect_writer_tasks_ordered` L447-470. Update six import sites.
- **Confidence:** high

## F-09: State symbol / colour tables duplicated across CLI and TUI (and for `DetectedState` as well)

- **Severity:** high
- **Location:** `src/commands/status.rs:25-47` (CLI symbols + ANSI rgb) vs `src/tui/widgets/table.rs:20-69` (TUI glyphs + `ratatui::Color`); `src/tui/action.rs:11-16` vs `src/tui/widgets/table.rs:71-76` (`is_graveyard`); `src/detect/mod.rs:33-46` `DetectedState::icon()` vs `src/tui/widgets/table.rs:43-69` glyph table.
- **Description:** `state_symbol(&TaskState)` is implemented twice with identical Unicode glyphs; `state_color` once as `ratatui::Color` and once as an ANSI `rgb(...)` escape; `is_graveyard(&TaskState)` twice with the same `matches!(...)` body. The RGB triples at `status.rs:40-46` shadow the named constants in `tui/theme.rs` (e.g. `rgb(120, 210, 120)` is `theme::OK`). The same drift exists for `DetectedState` — the TUI uses fancy glyphs, the `icon()` method returns ASCII, neither calls the other. Palette work currently requires touching 3-4 unrelated files.
- **Proposed remediation:** Hoist presentation onto the models: `impl TaskState { pub fn symbol(&self) -> &'static str; pub fn is_graveyard(&self) -> bool; pub fn semantic_color(&self) -> theme::Semantic }` where `Semantic` is an enum `{ Ok, Warn, Err, Done, Muted, Text }`. The TUI maps `Semantic -> ratatui::Color`, the CLI maps `Semantic -> rgb(...)`. Same treatment for `DetectedState::symbol()`; delete the unused `icon()`.
- **Confidence:** high

## F-10: `commands/status.rs` imports `format_tokens` from `tui::widgets::table`, reversing layering

- **Severity:** high
- **Location:** `src/commands/status.rs:11` — `use crate::tui::widgets::table::format_tokens;`
- **Description:** `format_tokens` is a pure `u64 → String` formatter with no ratatui dependency. Having the CLI `status` command import from `tui::widgets` makes the TUI a compile-time prerequisite of plain `agentrc status`, and it inverts the expected layering (TUI depends on commands/model, never the reverse). `tui/widgets/header.rs:6` also re-imports it back, confirming the helper wants a neutral home.
- **Proposed remediation:** Move `format_tokens` to a neutral `src/util.rs` (or `src/format.rs`) alongside `format_duration` (see F-16). Update both call sites. Optional: lift `format_duration` from `commands/status.rs:213-229` at the same time.
- **Confidence:** high

## F-11: `tui::app::handle_click` reverse-engineers `ui.rs` layout via hard-coded offsets

- **Severity:** high
- **Location:** `src/tui/app.rs:199-249`, coupled to `src/tui/ui.rs:62-73`
- **Description:** `handle_click` recomputes the click-to-row mapping by hard-coding `header(3)`, `workers_border(1)`, `column_header(1)` (L222-224), `detail(4) + keys(1) = 5 from bottom` (L239), and replicates the graveyard filter (L208-217) independently of the view layer. Any change to the `Layout::default().constraints([...])` block in `ui.rs` silently breaks clicks. The inline comment at L205-206 already flags the fragility. Classic feature envy — the method is data-hungry for layout but lives on `App`.
- **Proposed remediation:** Have `ui::render` (or the event loop in `commands/dashboard.rs`) cache the actual computed `Rect`s for the workers table / graveyard table / detail / events panels in a small `LayoutCache { workers: Rect, graveyard: Rect, detail: Rect, events: Rect }` kept on `App` or alongside the terminal. `handle_click(col, row)` then iterates the cache and asks "does this Rect contain (col, row)? which row within the table?". The magic-number arithmetic disappears.
- **Confidence:** high

## F-12: `render_workers` and `render_graveyard` are 54-line near-duplicates

- **Severity:** high
- **Location:** `src/tui/widgets/table.rs:221-274` (`render_workers`) and `src/tui/widgets/table.rs:276-329` (`render_graveyard`)
- **Description:** The two functions differ only in (a) the filter predicate (`!is_graveyard` vs `is_graveyard`), (b) the block title and border colour, (c) the highlight background, and (d) the selection-offset (`app.selected` vs `app.selected - active_count`). Everything else — rows construction, `max_tokens` computation, `make_header()` usage, `TableState` wiring — is copy/pasted. Any new column or sort has to be applied twice.
- **Proposed remediation:** Collapse into one helper `fn render_table(app, area, buf, flavour: &TableFlavour)` where `TableFlavour { title, border_color, highlight_bg, predicate: fn(&TaskState) -> bool, selection_offset: usize }`. `render_workers`/`render_graveyard` become three-line wrappers constructing the flavour and delegating.
- **Confidence:** high

## F-13: Redispatch-budget check duplicated with divergent error types

- **Severity:** high
- **Location:** `src/commands/amend.rs:58-65` vs `src/commands/respawn.rs:40-47`
- **Description:** Both commands gate on `status.redispatch_count >= config.max_redispatch_attempts`. `amend.rs` returns the structured `AppError::MaxRedispatchReached { task_id, max }`; `respawn.rs` calls `anyhow::bail!("task {} has reached max redispatch attempts ({})", ...)` with a plain string. Two callers of the same business rule, two error-API shapes. Both sites also duplicate the TaskStatus read/parse/mutate/write scaffold (amend.rs L48-56 + L85-89; respawn.rs L35-38 + L113-115) — see F-15.
- **Proposed remediation:** Either (a) extract `pub fn check_redispatch_budget(status: &TaskStatus, config: &OrchestratorConfig) -> Result<()>` returning `AppError::MaxRedispatchReached` on failure, or (b) add `impl TaskStatus { pub fn bump_redispatch(&mut self, max: u32) -> Result<()> }` that both increments and enforces (folds with F-15). Both call sites reduce to one line.
- **Confidence:** high

## F-14: Merge-loop arms in `integrate_in` duplicate 11-field `MergeResult` construction and event emission

- **Severity:** high
- **Location:** `src/commands/integrate.rs:286-412` (success arm L318-340, test-fail arm L341-381, conflict arm L382-412)
- **Description:** Each of the three arms builds a `MergeResult { ... }` literal with 11 fields, pushes to `results`, and emits a best-effort `crate::events::emit_info/emit_warn(... EventType::MergeSuccess|MergeTestFail|MergeConflict, ...)`. The only things that differ per arm are the status booleans, the per-arm populated vectors, and the message. This is the densest copy/paste in the file and the main reason it is 524 LOC.
- **Proposed remediation:** Pairs with F-07. Give `MergeResult` constructors: `MergeResult::merged(task_id, branch, commit_history)`, `MergeResult::conflict(task_id, branch, commit_history, files, overlapping)`, `MergeResult::test_failure(task_id, branch, commit_history, touched, stderr)`. Each constructor also records the appropriate event via a closure captured by `integrate_in`. Each arm shrinks to ~10 lines.
- **Confidence:** high

## F-15: `TaskStatus` read-modify-write ceremony inlined 6 times

- **Severity:** medium
- **Location:** `src/commands/spawn.rs:183-191`, `src/commands/respawn.rs:36-38, 109-115`, `src/commands/amend.rs:49-56, 85-89`, `src/commands/worker/done.rs:40-51`, `src/commands/worker/status.rs:44-105`, `src/commands/teardown.rs:82-99` (read-only)
- **Description:** Five mutating commands duplicate: `let content = fs::read_to_string(&status_file)?; let mut status: TaskStatus = serde_json::from_str(&content)?; /* mutate */; let json = serde_json::to_string_pretty(&status)?; fs::write(&status_file, json)?;`. Context messages differ per call site. All five sites share the JSON-pretty-print format choice, so any format change risks drift.
- **Proposed remediation:** Add `impl TaskStatus { pub fn load(path: &Path) -> Result<Self>; pub fn save(&self, path: &Path) -> Result<()>; pub fn update(path: &Path, f: impl FnOnce(&mut Self) -> Result<()>) -> Result<()> }`. Each site becomes `TaskStatus::update(&status_file, |s| { s.redispatch_count += 1; s.updated_at = Utc::now(); Ok(()) })?;`. Pairs with F-13.
- **Confidence:** high

## F-16: `format_duration` duplicated between `commands/status.rs` and `tui/widgets/table.rs`

- **Severity:** medium
- **Location:** `src/commands/status.rs:213-229` (`format_duration(secs: i64)`) vs `src/tui/widgets/table.rs:160-172` (inline)
- **Description:** `format_duration` is a tested public helper in `commands/status.rs`; `table.rs::build_row` reimplements exactly the same "under 60s / under 1h / else 1h m" branching inline at L164-170 without calling it. Outputs are identical except for the empty-input sentinel.
- **Proposed remediation:** Lift `format_duration` to a neutral `crate::util` / `crate::format` module (alongside `format_tokens` per F-10) and call from both places. The inline block in `table.rs` disappears.
- **Confidence:** high

## F-17: `frontmatter::update_field` and `upsert_field` are 95% identical

- **Severity:** medium
- **Location:** `src/fs/frontmatter.rs:55-81` (`update_field`) and `src/fs/frontmatter.rs:115-144` (`upsert_field`)
- **Description:** The two functions share `split_frontmatter`, `yaml_safe_value`, and the exact same `lines().map(...)` replacement loop. They differ only in how "key not found" is handled — `update_field` errors, `upsert_field` appends. Two bug surfaces for the same YAML line walk.
- **Proposed remediation:** Introduce a private `fn write_field(content: &str, key: &str, val: &str, allow_append: bool) -> Result<String>` and have both public entry points delegate. Alternatively make `upsert_field` the primitive and express `update_field` in terms of it with a presence check.
- **Confidence:** high

## F-18: `main.rs` uses `.expect()` for `current_dir` in the Amend arm alone

- **Severity:** medium
- **Location:** `src/main.rs:232`
- **Description:** `let cwd = std::env::current_dir().expect("cannot determine current directory");` is the one and only `.expect(...)` in `main.rs`. Every other `Commands::*` arm delegates to a `commands::*::run` helper that uses `?` with `.context(...)`. If `current_dir()` fails here, the process aborts with a raw panic rather than returning a formatted `anyhow::Error`. Worse, the Amend arm is the only one whose CLI handles `current_dir` in `main.rs` rather than in `commands::amend::run()`.
- **Proposed remediation:** Add `pub fn run(task_id: &str, brief: Option<&str>, message: Option<&str>) -> Result<()>` in `commands/amend.rs` that resolves `cwd` with `?` and calls `run_in`. `main.rs:227-234` collapses to one line matching the pattern of every other arm.
- **Confidence:** high

## F-19: Nine `AppError` variants declared but never constructed outside tests

- **Severity:** medium
- **Location:** `src/model/error.rs:7-17, 27-40, 45-52`
- **Description:** Only `NoActiveRun`, `RunAlreadyActive`, `TaskNotFound`, `TaskBriefParseError`, `StatusParseError`, `WorktreeExists`, `MaxRedispatchReached`, and `AmendSourceRequired` are constructed in production. `ConfigNotFound`, `InvalidStateTransition`, `DirtyBaseBranch`, `BranchExists`, `TmuxError`, `GitError`, `MergeConflict`, `TestFailure`, `NotInitialized` are orphans. `InvalidStateTransition` is especially notable because its matching guard `TaskState::can_transition_to` (see F-20) exists but is never called. `MergeConflict`/`TestFailure` were apparently superseded by `MergeResult`'s boolean fields and `anyhow::bail!` in `integrate.rs`, which is fine — but the dead variants suggest an unfinished migration.
- **Proposed remediation:** Either delete the unused variants or wire them up: `TmuxError`/`GitError` as the `bail!` target in `tmux::wrapper::run_tmux` and `git::wrapper::run_git`, `NotInitialized` for `OrchestratorPaths::config()` misses, `InvalidStateTransition` enforced in `worker::status::run_in` (see F-20). Deletion is the safer call for this audit — fewer surfaces to keep in sync.
- **Confidence:** high

## F-20: `TaskState::can_transition_to` is tested but never called; illegal transitions silently accepted

- **Severity:** medium
- **Location:** `src/model/task.rs:25-42` (definition + unit tests at `tests/model_test.rs:166-173`), consumer gap: `src/commands/worker/status.rs:37-108`
- **Description:** `can_transition_to` encodes a state machine (e.g. `Completed` cannot go back to `InProgress`) and is exercised by unit tests, but no production code calls it. `worker::status::run_in` overwrites `status.state = new_state` unconditionally, so a worker can force a `Completed` task back to `InProgress` via `agentrc worker status --state in_progress`. A guard that guards nothing, and a latent correctness issue.
- **Proposed remediation:** In `worker::status::run_in`, after loading the existing status and before the assignment, call `status.state.can_transition_to(&new_state)` and return `AppError::InvalidStateTransition { from, to }` when false. This folds F-19's dead variant, F-20, and the existing test into one change.
- **Confidence:** high

## F-21: `Tmux::build_*_args` static builders parallel the instance methods and drift independently

- **Severity:** medium
- **Location:** `src/tmux/wrapper.rs:22-130` (10 static `build_*_args`) vs `src/tmux/wrapper.rs:162-321` (instance methods using ad-hoc `&[&str]` literals)
- **Description:** Every instance method (`split_window`, `send_keys`, `kill_pane`, `move_pane`, `new_window`, `rename_window`, `current_window_name`, `capture_pane`, `set_pane_title`, `list_panes_with_titles`, `list_panes`) has a twin `build_*_args` static function, commented "Static command builders (testable without tmux)". The instance methods do NOT call the builders — they inline the arg literal. The builders are used only by `tests/tmux_test.rs`. If someone tweaks the real tmux call (e.g. adds `-d`) without touching the builder, tests pass but production is broken, or vice versa. The test coverage of the builder proves nothing about the instance method.
- **Proposed remediation:** Refactor each instance method to call its builder: `fn split_window(&self, w: &str) -> Result<String> { let args = Self::build_split_args(w); let refs: Vec<&str> = args.iter().map(String::as_str).collect(); self.run_tmux(&refs) }`. Optionally introduce `self.run_tmux_owned(&[String])` to avoid the collect. Alternatively, drop the builders and test `Tmux` via a `Command`-runner trait mock. Option 1 is the smaller change.
- **Confidence:** high

## F-22: `topo_sort` lives in `commands/plan.rs` but is imported by `integrate.rs`

- **Severity:** medium
- **Location:** `src/commands/plan.rs:239-275` (definition) vs `src/commands/integrate.rs:7,474` (consumer `use crate::commands::plan;`)
- **Description:** `integrate.rs` takes a module-level dependency on `plan.rs` to call `plan::topo_sort`. `detect_cycle` (plan.rs:141-233) is also a graph algorithm but is private to plan.rs. Both share data shapes (`HashMap<&str, Vec<&str>>`, in-degree counts) and should be co-located — they are graph algorithms, not plan-CLI helpers.
- **Proposed remediation:** Create `src/model/graph.rs` (or `src/model/dag.rs`) exporting `pub fn topo_sort(tasks: &mut Vec<TaskBriefFrontmatter>)`, `pub fn detect_cycle(briefs: &[TaskBriefFrontmatter]) -> Option<String>`, and optionally `pub fn validate_dag(briefs: &[TaskBriefFrontmatter]) -> Vec<String>` (the plan.rs:76-136 checks). `plan::validate_briefs` becomes a thin shim; `integrate::collect_writer_tasks_ordered` calls `graph::topo_sort` without depending on a CLI sibling.
- **Confidence:** high

## F-23: Heartbeat timeout hardcoded to 120 in two places, ignoring `OrchestratorConfig`

- **Severity:** medium
- **Location:** `src/commands/status.rs:142` (`find_stale_heartbeats(project_root, 120)?`) and `src/commands/watch.rs:14` (`const HEARTBEAT_TIMEOUT_SEC: u64 = 120;`)
- **Description:** `OrchestratorConfig::heartbeat_timeout_sec` exists, defaults to 120, and is correctly read by `tui/app.rs:103` and `resume.rs:46`. But `commands/status::format_tty` and `commands/watch::watch` use the hardcoded `120`, so an operator who tunes `heartbeat_timeout_sec` sees inconsistent stale-heartbeat behaviour depending on which command they run.
- **Proposed remediation:** In `format_tty`, load the config (via F-02/F-05 helpers) and pass `config.heartbeat_timeout_sec`. In `watch.rs`, either read the config in `watch()` and pass through to `watch_with_receiver`, or remove the module constant entirely in favour of the config value.
- **Confidence:** high

## F-24: Manual ANSI / ASCII table printing duplicated across 5 command outputs

- **Severity:** medium
- **Location:** `src/commands/status.rs:140-205`, `src/commands/integrate.rs:78-118`, `src/commands/checkpoint.rs:179-187,228-262`, `src/commands/run.rs:29-32`
- **Description:** Every CLI listing rolls its own `println!("{:<8} {:<14} ...", ...)` with hand-tuned column widths (`:<8`, `:<14`, `:<12`, `:<10`, `:<25` in status.rs; `:<8`, `:<30`, `:<10` in integrate.rs; `:<20`, `:<8`, `:<6`, `:<14`, `:<30` in checkpoint.rs) and bespoke separator bars (`"-".repeat(105)`, `"-".repeat(72)`, `"-".repeat(60)`, `"-".repeat(70)`). Width changes mean editing header + separator + every row literal. ANSI colour in `status.rs:176-181` is interleaved with alignment — easy to break.
- **Proposed remediation:** Add a small internal helper `src/cli/table.rs` (~60 LOC): `struct AsciiTable { columns: Vec<Column>, rows: Vec<Vec<StyledCell>> }` with `Column { header, width, align }` and `StyledCell { text, color }`, and a `print_tty(&self)` method. Alternatively adopt a small dev-dep like `prettytable` or `tabled`. Not a large abstraction but collapses five copies of the same printf ceremony.
- **Confidence:** medium

## F-25: `App::refresh` drives six orthogonal passes with implicit ordering

- **Severity:** medium
- **Location:** `src/tui/app.rs:100-139`
- **Description:** `refresh` does six unrelated things in a single 40-LOC linear block: collect statuses, collect stale heartbeats, scan every pane for detected state, scan panes for tokens, scan orchestrator pane for its tokens, tail recent events, clamp selection, update anim activity. Individual passes are simple but implicit ordering (e.g. anim activity is computed from `active_count`, which needs `statuses` loaded first) is load-bearing and undocumented. Adding a seventh pass invites quiet bugs.
- **Proposed remediation:** Decompose into named methods on `App`: `fn reload_statuses`, `fn reload_heartbeats`, `fn scan_panes`, `fn scan_orchestrator_tokens`, `fn reload_events`, `fn clamp_selection`. `refresh` becomes an ordered orchestrator calling them. Each helper is individually unit-testable with a mock `Tmux`.
- **Confidence:** medium

## F-26: `integrate::append_log` and `events::emit` duplicate the append-open pattern

- **Severity:** medium
- **Location:** `src/commands/integrate.rs:515-524` vs `src/events.rs:11-27`
- **Description:** `integrate::append_log` opens `.orchestrator/<run>/integration.log` via `OpenOptions::new().create(true).append(true).open(...)` and appends plain text lines; `events.rs::emit` does the identical `OpenOptions` dance to append JSON to `events.jsonl`. Both swallow the IO error. The artefacts are legitimately different (one human-readable, one machine-parsed JSONL), but the IO primitive is shared.
- **Proposed remediation:** Extract `fn append_line(path: &Path, line: &str) -> io::Result<()>` into `src/fs/mod.rs` (or a new `fs::logs`). Both callers use it; each preserves its own format. Consider adding an `AtomicWrite` helper at the same time for JSON status files (F-15).
- **Confidence:** medium

## F-27: `worker::status::parse_state` and `TaskState::fmt` manually mirror serde

- **Severity:** medium
- **Location:** `src/commands/worker/status.rs:111-122` (`parse_state`) and `src/model/task.rs:44-56` (`impl Display`)
- **Description:** `TaskState` uses `#[serde(rename_all = "snake_case")]`, but both the `Display` impl and `worker::status::parse_state` hand-roll the mapping. Adding a variant requires updating the enum, the `Display` arm, and `parse_state` — with silent divergence if any is forgotten. Tests at `tests/model_test.rs` cover transitions but not the Display↔serde round-trip.
- **Proposed remediation:** Implement `Display` via `serde_json::to_string(self)` stripped of quotes (one allocation per call — acceptable for CLI printing), or adopt `strum::{EnumString, Display}` derives if a small dep is acceptable. Implement `FromStr` once delegating to `serde_json::from_str`, and have `worker::status::run_in` use it. Add a unit test asserting round-trip `Display → FromStr → Display` equality for every variant.
- **Confidence:** medium

## F-28: Unused import in `tui/app.rs` test module

- **Severity:** low
- **Location:** `src/tui/app.rs:255`
- **Description:** Clippy reports `warning: unused import: crate::model::event::OrcEvent` at `src/tui/app.rs:255:9`, inside `#[cfg(test)] mod tests`. Dead import, easy fix.
- **Proposed remediation:** Delete the line. Rust's unused-import lint would catch this in a default `cargo check` if elevated to error in `Cargo.toml [lints]`.
- **Confidence:** high

## F-29: `model::worker::PaneId` is completely dead code

- **Severity:** low
- **Location:** `src/model/worker.rs:1-12` (entire file)
- **Description:** `PaneId(pub String)` and its `Display` impl are defined but never referenced in `src/` or `tests/`. Every pane id in the codebase flows as a bare `String` (e.g. `TaskStatus::pane_id: Option<String>`, `Tmux::send_keys(&self, pane_id: &str, ...)`). The spec at `docs/agentrc-implementation-spec.md` also promises a `WorkerState` that never shipped.
- **Proposed remediation:** Delete `src/model/worker.rs` and remove `pub mod worker;` from `src/model/mod.rs`. Anyone wanting a typed pane id can reintroduce it alongside the refactor that adopts it.
- **Confidence:** high

## F-30: `Tmux::split_right`, `split_below`, and `wait_for_channel` are uncalled

- **Severity:** low
- **Location:** `src/tmux/wrapper.rs:175-201` (`split_right`, `split_below`) and `src/tmux/wrapper.rs:318-321` (`wait_for_channel`)
- **Description:** Three instance methods on `Tmux` have zero call sites in `src/` or `tests/`. `signal_channel` at L312 IS used (by `worker/done.rs`), so `wait_for_channel` was presumably the orchestrator side of a handshake that never materialised. Dead API surface.
- **Proposed remediation:** Delete the three methods. If the wait-for handshake is planned for a future phase, note it in the relevant design doc rather than leaving untested methods on the wrapper.
- **Confidence:** high

## F-31: `pub` items that should be `pub(crate)` / `pub(super)`; test-only helpers lack markers

- **Severity:** low
- **Location:** `src/commands/worker/mod.rs:18` (`resolve_project_root`), `src/commands/spawn.rs:20,33,59,82,87`, `src/commands/install.rs:54,138`, `src/commands/plan.rs:76,141,239`, `src/commands/respawn.rs:140,199`
- **Description:** `worker::resolve_project_root` is `pub` but called only within the `worker::*` siblings (via `super::`) — should be `pub(super)`. A broader pattern: many `pub` helpers are exported only because integration tests under `tests/` need them (plain `pub(crate)` is insufficient for `tests/`); nothing in the doc comments flags them as "test-only", so a future contributor could accidentally treat them as stable public API.
- **Proposed remediation:** (1) Change `resolve_project_root` to `pub(super)`. (2) For the test-exposed helpers, add a one-line doc marker: `/// _Exposed for integration tests — not part of the stable public API._`. Alternatively put them behind `#[cfg(any(test, feature = "test-api"))]`; the doc marker is the cheapest fix.
- **Confidence:** high

## F-32: Branch / pane-title / `.orchestrator/` literals scattered across modules

- **Severity:** low
- **Location:** `src/commands/spawn.rs:143,173`; `src/commands/respawn.rs:78,173`; `src/fs/bus.rs:17`; `src/tui/anim/widget.rs:62` (the `.orchestrator/` literal)
- **Description:** Three naming conventions appear as inline `format!(...)` or bare string literals in multiple files: `orc/<id>-<slug>` (branch), `orc:<id>:<slug>` (pane title), and `".orchestrator"` (runtime-state directory). A brand or path rename requires grep-and-replace.
- **Proposed remediation:** Add helpers in `src/model/task.rs` (or a new `src/model/naming.rs`): `pub fn default_branch(id: &str, slug: &str) -> String` and `pub fn pane_title(id: &str, slug: &str) -> String`. Add `pub const ORCHESTRATOR_DIR: &str = ".orchestrator";` in `src/fs/bus.rs` and use it wherever the literal appears.
- **Confidence:** medium

## F-33: `yaml_safe_value` runs 16 sequential `contains()` calls against the same string

- **Severity:** low
- **Location:** `src/fs/frontmatter.rs:84-112`
- **Description:** `yaml_safe_value` passes over the input 16 times, once per special character (`%`, `:`, `#`, etc). Each `value.contains(c)` is O(n). Performance is irrelevant for short frontmatter values, but the code is hard to audit — "did we already cover `*`?" — and embeds YAML 1.2 escape policy in application code.
- **Proposed remediation:** Replace with `const UNSAFE: &[char] = &['%', ':', '#', '{', '}', '[', ']', ',', '&', '*', '!', '|', '>', '\'', '"', '`', '@']; value.chars().any(|c| UNSAFE.contains(&c)) || value.starts_with(' ') || value.ends_with(' ')`. One pass, easier to eyeball.
- **Confidence:** high

## F-34: `spawn::setup_worktree` takes a dead `_slug` parameter

- **Severity:** low
- **Location:** `src/commands/spawn.rs:59-78`
- **Description:** `setup_worktree(... , _slug: &str, branch: &str, ...)` never uses `_slug` — the leading underscore is Rust's "intentionally unused" convention, but the parameter is still part of the signature and every caller (including `tests/happy_path.rs`, `tests/spawn_test.rs`, `tests/fault_injection.rs`) has to pass a slug that gets ignored. The branch name comes entirely from `branch`. The function's docstring at L55-58 already omits `slug`, so no doc update is needed.
- **Proposed remediation:** Delete the parameter. Update the four test callers.
- **Confidence:** high

## F-35: Duplicate step comment in `spawn::run` (two step 9s)

- **Severity:** low
- **Location:** `src/commands/spawn.rs:182,193`
- **Description:** `spawn::run` is documented as a numbered sequence. Step 7 is at L172 (title), step 8 at L176 (brief update), then two step-9 comments: L182 (`// 9. Update status with pane_id and pane_title`) and L193 (`// 9. Retile, cd to worktree, launch heartbeat + claude, seed prompt`). The numbering is the only structural scaffolding in a 140-line function and it is already out of sync.
- **Proposed remediation:** Renumber the second `9` to `10`, or drop the numbers entirely and rely on the comment text. Even better, extract the tmux-launch block L193-232 into `fn launch_worker(tmux, pane_id, ...) -> Result<()>` — which also dissolves most of F-06's duplication with `respawn::run_in`.
- **Confidence:** high

## F-36: `Classification::Writer` branching implicit across spawn / integrate / audit

- **Severity:** low
- **Location:** `src/commands/spawn.rs:142-153,202-207`, `src/commands/integrate.rs:459`, `src/audit.rs:50-53`
- **Description:** The rule "writers have branches and worktrees, readers do not" is encoded separately in every consumer via direct `match brief.classification` branches. Spawn picks worktree-vs-project-root twice in the same function (L142-153 and L202-207). Integrate filters to writers at L459. Audit asserts `brief.branch.is_some()` at L50-53. Any future classification (e.g. a third role, or a writer that should stay in-tree) requires touching all callers.
- **Proposed remediation:** Add methods on `TaskBriefFrontmatter`: `is_writer(&self) -> bool`, `expected_branch(&self) -> Option<String>` (Some for writer with synthesised default, None for reader), `work_dir(&self, project_root: &Path, run: &RunPaths) -> PathBuf` (worktree for writer, project_root for reader). Each consumer reduces to a method call.
- **Confidence:** medium

## F-37: Pervasive `uninlined_format_args` in test modules (~30 occurrences)

- **Severity:** low
- **Location:** `tests/integrate_test.rs` (7 sites), `tests/layout_test.rs` (8), `tests/audit_test.rs` (6), `tests/happy_path.rs` (11), plus `src/tui/anim/shapes.rs:151` and `src/tui/anim/mod.rs:119` in `#[cfg(test)]` blocks (`float_cmp` on unit-vector asserts — intentional — and `unchecked_time_subtraction` — test-only).
- **Description:** `cargo clippy --all-targets -- -W clippy::pedantic` reports 361 warnings of which ~356 are duplicate `uninlined_format_args` across test targets (e.g. `format!("%{}", i)` → `format!("%{i}")`). None affect behaviour; none are in production paths. The three non-format-arg `src/` warnings (`unused import` F-28; `float_cmp` in `shapes.rs::cube_vertices_are_unit` test; `unchecked_time_subtraction` in `tick_advances_angle` test) are all test-only.
- **Proposed remediation:** One-shot mechanical fix via `cargo clippy --fix --tests -p agentrc -- -W clippy::uninlined_format_args`. For the `float_cmp` lint at `shapes.rs:151`, either accept and gate with `#[allow(clippy::float_cmp)]` (the assert is correct — cube vertices are exact ±1.0 by construction) or rewrite as `(v.0.abs() - 1.0).abs() < f64::EPSILON`. For the `unchecked_time_subtraction` at `anim/mod.rs:119`, swap to `Instant::now().checked_sub(Duration::from_millis(200)).unwrap()` — test panics on sub-200ms-uptime machines otherwise.
- **Confidence:** high
