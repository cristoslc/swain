---
source_run: 20260412T211612-comprehensive-audit
triage_date: 2026-04-12
bucket_id: 118
status: deferred (never dispatched in phase 2)
totals:
  total: 80
  by_domain:
    security: 10
    performance: 5
    rust-impl: 9
    code-quality: 10
    product-spec: 7
    test-coverage: 39
---

# Audit Backlog — Deferred Low-Severity Findings

Findings from the 2026-04-12 comprehensive audit sweep that triage
classified as severity `low` and deferred to this backlog instead of
dispatching a fix worker. Revisit as follow-up work or during the next
audit sweep.

Each line references the original report at `docs/audits/<domain>.md`.
Full descriptions, remediations, and file:line citations live in those
reports.

## security (10)

- **F-23** — `let _ = ...` cleanup silence. (`src/commands/teardown.rs` area)
- **F-24** — `collect_statuses` CLI-vs-TUI inconsistency.
- **F-25** — `events::emit` uses `writeln!` without fsync.
- **F-26** — events tail allocation (absorbed into performance F-01 fix).
- **F-27** — `git.branch_exists` `unwrap_or_default` fallbacks.
- **F-28** — `format_tty` doesn't honor `NO_COLOR`.
- **F-29** — `update_claude_md` non-atomic write.
- **F-30** — `run::create_in` leaves orphan directories on partial failure.
- **F-31** — `.expect("current_dir")` in main.rs (absorbed into rust-impl F-15 fix).
- ~~F-32~~ — recalibrated to medium during triage; handled by bucket 103.

## performance (5)

- **F-12** — `depth_to_style` called per terminal cell on render.
- **F-17** — animation `tick()` still fires when widget is hidden.
- **F-19** — `format_event_line` recomputed per render pass.
- **F-20** — `handle_click` recomputes row counts.
- **F-21** — `render_info` per-row dot-leader string allocation.
- **F-22** — `events::tail` drain optimization opportunity.

## rust-impl (9)

- **F-17** — `useless_format` pedantic lint (recalibrated from high).
- **F-36** — `audit.rs` placement asymmetric with other domain modules.
- **F-37** — `classify_commit::CommitKind` public scope too wide.
- **F-38** — `get_field` error swallowed.
- **F-39** — duplicate workers window constant.
- **F-40** — events tail allocation (absorbed into performance F-01 fix).
- **F-41** — `TaskState` has three parallel mappings (serde/manual/display).
- **F-42** — multi-pane scan in `App::refresh` (absorbed into code-quality F-25).
- **F-44** — `toggle_events` widget test coverage gap.

## code-quality (10)

- **F-28** — unused import in test module.
- **F-29** — `PaneId` dead code path.
- **F-30** — `Tmux` dead methods.
- **F-31** — `pub` items that should be `pub(crate)`.
- **F-32** — "workers" and similar string literals scattered.
- **F-33** — `yaml_safe_value` uses 16 `.contains()` checks.
- **F-34** — `spawn::setup_worktree` dead `_slug` parameter.
- **F-35** — duplicate "step 9" comment in spawn (absorbed into rust-impl F-11).
- **F-36** — implicit `Classification` branching (kept as medium in bucket 111).
- **F-37** — `uninlined_format_args` in tests.

## product-spec (7)

- **F-37** — `integrate --dry-run` under-documented.
- **F-38** — `layout collate` under-documented.
- **F-39** — no `CONTRIBUTING.md` or `CHANGELOG.md`.
- **F-40** — README command syntax mixed styles.
- **F-41** — "integrate" vs "merge" verb inconsistency.
- **F-42** — README has a second architecture diagram that duplicates the first.
- **F-43** — typos and em-dash style drift.

## test-coverage (39)

Test-coverage findings at severity `low` represent coverage gaps that
are cosmetic, or already-covered by stronger findings, or dead code.
They are not a coverage emergency but a follow-up pass would polish
the harness:

- **F-079** — events/audit CLI wrappers untested.
- **F-080** — amend pane-notification + checkpoint event untested.
- **F-081** — absorbed into code-quality F-05.
- **F-082** — `dashboard::run` no smoke test.
- **F-083** — `append_log` error paths (absorbed into code-quality F-26).
- **F-084** — integrate dry-run vs real divergence untested.
- **F-085** — `layout::run` CLI untested.
- **F-086** — respawn pane-kill silencing untested.
- **F-088** — watch non-json files untested.
- **F-089** — watch seed malformed (absorbed into rust-impl F-09).
- **F-090** — worker::done tmux-bell untested.
- **F-091** — heartbeat daemon loop untested.
- **F-092** — notes growth (absorbed into security F-32 merge).
- **F-093** — `result::run_in` overwrite-vs-append semantics untested.
- **F-094** — emit on missing run dir.
- **F-095** — `emit_warn` vs `Error` severity inconsistency.
- **F-096** — `RunPaths::scaffold` partial-state recovery.
- **F-097** — `upsert_field` missing delimiters.
- **F-098** — `get_field` absent-vs-empty distinction.
- **F-099** — `RunMetadata.archived` dead field.
- **F-100** — `RunMetadata::slug` edge cases.
- **F-101** — `PaneId` dead (overlaps code-quality F-29).
- **F-102** — tmux static builder constants.
- **F-103** — `AnimState::tick` rate-limit semantics.
- **F-104** — anim widget `render_info` untested.
- **F-105** — `draw_line_dotted` untested.
- **F-106** — `App::refresh` error-path.
- **F-107** — git `--local` flag.
- **F-108** — `classify_*` tests in integration binary.
- **F-109** — `mouse_event` compile-time check.
- **F-110** — `parse_tokens_k_format` edge cases.
- **F-111** — `parse_tokens_from_text` None path.
- **F-112** — integrate brief-duplication (absorbed into rust-impl F-35).
- **F-113** — `validate_duplicate_ids` ambiguous.
- **F-114** — `is_err()` without variant check.
- **F-115** — teardown fs failure path.
- **F-116** — `worker_note` "202" timestamp handling.
- **F-117** — `Severity::Error` unused variant (absorbed into test-cov F-095).
- **F-118** — `TaskBrief` has no schema_version field.

---

## How to revisit

When touching any of the files mentioned above, reference the relevant
finding here and fix it opportunistically. A future audit sweep will
re-survey and either re-flag or confirm the finding is stale.

Source triage document (internal, not committed): `/tmp/triage-2026-04-12.md`.
