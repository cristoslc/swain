---
domain: product-spec
task_id: "005"
auditor_pipeline: "voltagent-biz:product-manager + voltagent-biz:technical-writer"
scope:
  - README.md
  - CLAUDE.md
  - skill/agentrc/*
  - docs/*.md
  - src/main.rs (cross-reference)
  - src/commands/*.rs (cross-reference for spec claims)
  - src/model/config.rs (cross-reference for config claims)
generated_at: 2026-04-12
---

# Phase 1 Audit — product-spec

## Totals by severity

| Severity | Count |
|---|---|
| critical | 4  |
| high     | 14 |
| medium   | 18 |
| low      | 7  |
| **total** | **43** |

## Executive summary

Two specialists (product-manager and technical-writer) audited the user-facing and
contract-level artifacts of the agentrc repository against the implemented binary.
The most load-bearing failure is mechanical, not cosmetic: **`agentrc spawn` never
loads `skill/agentrc/worker-seed.txt`** — it hard-codes a minimal 4-line seed in
`src/commands/spawn.rs`. Every worker contract clause the repo carefully encodes
(TDD invocation, git allowlist, heartbeat daemon notice, reader/writer discipline,
subagent git rule) is therefore never actually injected into spawned workers.
The only reason things appear to work is that `agentrc init` also writes worker
directives into the project's `CLAUDE.md`, which Claude Code auto-loads — but that
silent `CLAUDE.md` modification is itself undocumented in the README (F-04), and
the root `CLAUDE.md` has drifted from the template it should be regenerated from
(F-18), so the two sources of truth have diverged.

Beyond the worker-contract failure, the README's command catalog is incomplete in
both directions: `events` is implemented but not advertised (F-05); `auto_respawn`
is advertised but not implemented (F-02); `checkpoint list`, `--force` on
`teardown`, `heartbeat_interval_sec`, and `worker_claude_args` are documented in
some places and missing in others. The Quick Start sequence in the README
(F-03) is technically incomplete: running the documented commands produces a
`.orchestrator/` with no active run, and every subsequent command errors until
the skill's bootstrap fires `agentrc run create`. The docs under `docs/*` are a
mix of implemented-but-labelled-draft specs and superseded design docs that do
not label themselves as superseded (`tmux-workflow-design-spec.md`,
`agentrc-phase{1,3}-plan.md`, `ascii-animations-design.md`).

Finally, load-bearing concepts (`writer` vs `reader`, `run` vs `task`, the
skill-symlink mechanism that powers "start a Claude Code session and describe
your goal") are used without definition in README, SKILL.md, and the worker
prompts. A new user has no canonical glossary to recover from. A new orchestrator
session has no Terminology block in SKILL.md to ground its dispatch decisions.

Clean areas: the README ASCII architecture diagram, the image links, the GitHub
URL, the `run create/list/archive` surface, the `worker status/note/result/done/
heartbeat` surface, the `plan validate` logic, the `checkpoint save/restore`
JSON schema, and the `worker-seed.txt` git-allowlist section (once it is actually
loaded) are consistent and non-drifting.

---

## F-01: `agentrc spawn` ignores `skill/agentrc/worker-seed.txt` entirely
- **Severity:** critical
- **Location:** `src/commands/spawn.rs:87-94` vs `skill/agentrc/worker-seed.txt:1-25`
- **Description:** The skill ships a 25-line `worker-seed.txt` defining the full worker contract (TDD invocation of `superpowers:test-driven-development`, reader/writer discipline, heartbeat daemon notice, git allowlist, forbidden-operations list, subagent rule, how to signal blocked, how to signal done). The implementation spec (`docs/agentrc-implementation-spec.md:362`) says "Generated from `worker-seed.txt` template with substitutions." But `src/commands/spawn.rs:87-94` hardcodes a minimal 4-line seed: "You are worker {task_id}. Read your task brief at `{brief_path}` and begin work. Use `agentrc worker status ... in_progress`. Use `agentrc worker heartbeat`. Use `agentrc worker done` when finished." A grep for `worker-seed` in `src/` returns zero hits — the template file is never loaded. Every TDD, git-protocol, and reader/writer invariant the docs present as a worker contract is invisible to real workers; they rely entirely on the project's `CLAUDE.md` being present in the worktree, which is only populated if `agentrc init` has run in that project.
- **Proposed remediation:** Either (a) load `~/.claude/skills/agentrc/worker-seed.txt` in `generate_seed_prompt`, do `{{TASK_ID}}`/`{{BRIEF_PATH}}` substitutions, and fall back to the inline string only if the file is missing; or (b) delete `worker-seed.txt` and document that the contract lives in `CLAUDE.md` + the brief. Option (a) matches the implementation spec and is the stated design. Also update `src/commands/respawn.rs:205-213` (`generate_resume_seed`) to use a resume-specific template file for consistency.
- **Confidence:** high

## F-02: README advertises `auto_respawn` config field that does not exist
- **Severity:** critical
- **Location:** `README.md:114` vs `src/model/config.rs:24-51`
- **Description:** The README Configuration table lists `| auto_respawn | true | Respawn dead workers automatically |`. `OrchestratorConfig` has no `auto_respawn` field — grep confirms zero occurrences in `src/`. A user who copies this value into `.orchestrator/config.json` will have it silently ignored (serde drops unknown keys by default on this struct layout). Worse, the promise "Respawn dead workers automatically" is flatly false — `respawn` is a manual command, and SKILL.md explicitly says "Redispatch requires user confirmation. Never kill and respawn a worker without the user explicitly approving" (`SKILL.md:100`). Phase 3 design (`docs/agentrc-phase3-design.md:8`) calls out "Auto-Respawn" as Track B, but the implemented `respawn.rs` requires an explicit `agentrc respawn <task-id>` invocation.
- **Proposed remediation:** Remove the `auto_respawn` row from `README.md:114`. (If the product owner wants the feature, add the field to `OrchestratorConfig` and wire an auto-respawn loop — but the stated SKILL.md invariant contradicts automation, so removal is the intended direction.) While editing, also align the Configuration table with what init actually writes.
- **Confidence:** high

## F-03: README Quick Start produces a non-functional `.orchestrator/` and skips the symlink explainer
- **Severity:** critical
- **Location:** `README.md:58-73` vs `src/commands/init.rs:16-61`, `src/commands/run.rs:51-85`, `src/commands/install.rs`
- **Description:** Two conjoined gaps. (1) The Quick Start says `cargo install --path . && agentrc install && cd /path/to/your/project && agentrc init`, then "Start a Claude Code session and describe your goal. The orchestrator takes it from there." Running `agentrc init` alone creates only `.orchestrator/runs/` + `config.json` + `.gitignore` entry + `CLAUDE.md`; it does NOT create an `active` symlink, `plan.md`, or any runnable scaffold. Every subsequent command (`spawn`, `status`, `integrate`, `resume`, `checkpoint`, `events`, `plan validate`, `run archive`, `watch`, `teardown`, `amend`, `dashboard`'s data load) bails with `AppError::NoActiveRun` until `agentrc run create --slug <name>` runs. (2) `agentrc install` symlinks `<repo>/skill/agentrc/` into `~/.claude/skills/agentrc/` — this is what makes "start a Claude Code session and describe your goal" work — but the README never mentions it, so a user whose symlink fails has no recovery path, and the reader has no mental model for how the orchestrator shows up in the subsequent Claude Code session. Only `docs/agentrc-implementation-spec.md:78, 579-583` documents the symlink.
- **Proposed remediation:** After the `agentrc install` command block in `README.md:65`, insert a short verification line: "`agentrc install` symlinks this repo's `skill/agentrc/` into `~/.claude/skills/agentrc/`, which Claude Code auto-discovers. Verify with `ls -la ~/.claude/skills/agentrc`. Running `git pull` on this repo updates the installed skill automatically." At `README.md:73`, replace "Start a Claude Code session and describe your goal. The orchestrator takes it from there." with: "Start a Claude Code session in your project. The agentrc skill activates automatically; describe your goal. The orchestrator will run `agentrc run create --slug <name>` and propose a plan for your approval before spawning any workers." Also teach `status`/`resume`/`dashboard` to print a friendlier "No active run — orchestrator should run `agentrc run create --slug <name>` first" hint rather than raw `AppError::NoActiveRun`.
- **Confidence:** high

## F-04: `agentrc init` silently modifies the project's `CLAUDE.md`
- **Severity:** critical
- **Location:** `README.md:68-80` vs `src/commands/init.rs:49, 83-144`
- **Description:** `agentrc init` appends (or replaces) an `<!-- agentrc:begin -->` / `<!-- agentrc:end -->` block inside `CLAUDE.md` at the project root, creating the file if absent. This is a material change to a file many users already version-control and carefully maintain. The README says only "Scaffold `.orchestrator/`, detect test command" (line 80) — no mention of `CLAUDE.md` edits. A user running `agentrc init` on an existing project finds their `CLAUDE.md` modified without warning, which is surprising and undermines trust. (It is also the mechanism that makes worker directives appear to spawned workers, so it is not optional.)
- **Proposed remediation:** Update the `init` row in the README command table (line 80) to: `` `init` | Scaffold `.orchestrator/`, detect test command, inject agentrc worker directives into `CLAUDE.md` (creates file if missing) ``. Add a brief paragraph after the `agentrc init` command block (around line 72) noting: "`agentrc init` also writes an `<!-- agentrc:begin -->`/`<!-- agentrc:end -->` block into your project's `CLAUDE.md`, creating the file if absent. The block contains worker directives and is safe to re-run — existing markers get replaced in place."
- **Confidence:** high

---

## F-05: `events` command implemented but not in README or SKILL.md reference
- **Severity:** high
- **Location:** `src/main.rs:88-93`, `src/commands/events.rs:1-29` vs `README.md:77-95`, `skill/agentrc/SKILL.md:28-43`
- **Description:** `agentrc events [--tail N]` is a full subcommand that prints the run's event log (spawned, merge_started, merge_success, merge_conflict, merge_test_fail, checkpoint_saved, respawned, etc.). It is a primary observability surface. README's Commands table does not list it, and SKILL.md's Quick Reference does not list it either. Users and the orchestrator LLM will never discover this command by reading the docs.
- **Proposed remediation:** Add a row `| events [--tail N] | Show the run event log (default tail=20) |` to README Commands table (`README.md:95`) AND SKILL.md Quick Reference (`skill/agentrc/SKILL.md:42`). The docstring in `src/main.rs:88` says "Show the event log" — echo that.
- **Confidence:** high

## F-06: SKILL.md Quick Reference omits `amend`, `audit`, `events`, `watch`, `plan validate`
- **Severity:** high
- **Location:** `skill/agentrc/SKILL.md:26-43` vs `src/main.rs:57-98`
- **Description:** SKILL.md's Quick Reference is the orchestrator LLM's primary view of the CLI surface. It omits five commands that are fully implemented: `amend <task-id>` (referenced in SKILL.md's Phase 3 monitor section implicitly as "update task brief with conflict addendum"), `audit <task-id>` (TDD audit), `events [--tail N]`, `watch` (explicitly documented in README), and `plan validate`. The orchestrator cannot use what it cannot see; SKILL.md's "reactive integration" phase tells the orchestrator to "update task brief with conflict addendum" without pointing it at `amend` (`src/commands/amend.rs:22-103`).
- **Proposed remediation:** Add rows for all five commands to SKILL.md Quick Reference with one-line purposes. Then update `### Phase 3: MONITOR + INTEGRATE` step 2e to explicitly suggest `agentrc amend <task-id> --message "..."` on conflict rather than leaving it as hand-waving prose.
- **Confidence:** high

## F-07: SKILL.md "never use `tmux capture-pane`" contradicted by dashboard's detection path
- **Severity:** high
- **Location:** `skill/agentrc/SKILL.md:61` vs `src/commands/dashboard.rs` + `src/detect/` (per `docs/agentrc-phase3-design.md:91-99`)
- **Description:** SKILL.md says "Always use agentrc commands to check worker state — never use raw `tmux capture-pane` or `tmux list-panes`. The CLI is the interface." Phase 3 design adds `Tmux::capture_pane` and does passive detection by scanning scrollback — exactly the thing SKILL.md forbids. The dashboard does it on every refresh tick. The directive is aimed at the orchestrator LLM while the dashboard does it internally, so there's no functional conflict — but the absolute wording creates a confusing mental model: `capture-pane` is trusted in one layer and forbidden in another.
- **Proposed remediation:** Soften SKILL.md:61 to "For worker state queries, always use `agentrc status`/`dashboard` rather than raw tmux — the binary normalizes across panes and worktrees." Do not ban `capture-pane` outright; the dashboard depends on it.
- **Confidence:** high

## F-08: `CLAUDE.md` Worker Contract omits heartbeat-daemon notice
- **Severity:** high
- **Location:** `CLAUDE.md:23-36`, `skill/agentrc/claude-md-section.md` (absent) vs `skill/agentrc/worker-seed.txt:12`
- **Description:** `worker-seed.txt:12` says "A heartbeat daemon is running in the background. Do not touch it." This is load-bearing — without it, a worker might run `agentrc worker heartbeat` manually, duplicate the daemon, or kill the existing one. The root `CLAUDE.md` Worker Contract has 9 numbered items and omits this note. `claude-md-section.md` (the template `agentrc init` injects) also omits it. Combined with F-01 (worker-seed.txt is never loaded into workers), no worker is ever told about the heartbeat daemon.
- **Proposed remediation:** Add a line to `claude-md-section.md` Worker Contract: "A heartbeat daemon is running in the background — do not touch it." Sync to the root `CLAUDE.md`. Once F-01 is fixed this is redundant but still useful as a second signal.
- **Confidence:** high

## F-09: Root `CLAUDE.md` contradicts `worker-seed.txt` on TDD dispatch stack
- **Severity:** high
- **Location:** `CLAUDE.md:8-21` vs `skill/agentrc/worker-seed.txt:6`
- **Description:** `worker-seed.txt:6` says writers should "invoke superpowers:test-driven-development and follow TDD rigorously. Red -> green -> refactor." Root `CLAUDE.md`'s Subagent Dispatch section tells workers to dispatch `voltagent-qa-sec:test-automator` for test writing and `voltagent-lang:rust-engineer` for implementation — a completely different subagent stack. Moreover, `CLAUDE.md` says "Do NOT write Rust code, tests, or complex logic directly. Dispatch to the appropriate specialist." That conflicts with `superpowers:test-driven-development` which prescribes the worker writing tests inline. Both prompts flow into the same worker session once F-01 is fixed.
- **Proposed remediation:** Decide canonical stack. If voltagent is current (per memory notes), update `worker-seed.txt:6` to: "For writer tasks: dispatch `voltagent-qa-sec:test-automator` for tests and `voltagent-lang:rust-engineer` for implementation; follow TDD rigorously (red → green → refactor at the specialist level, not the worker level)." Or, if agent.rc repo self-hosts a different stack than user projects, make that distinction explicit.
- **Confidence:** high

## F-10: `spawn.rs` send-keys sequence diverges from spec; heartbeats outlive workers
- **Severity:** high
- **Location:** `docs/agentrc-implementation-spec.md:357` vs `src/commands/spawn.rs:211-232`
- **Description:** Spec says the pane launches via `agentrc worker heartbeat --task 001 & HB=$!; claude; kill $HB 2>/dev/null; exit`. This ensures heartbeat dies when claude exits and the pane auto-closes. Actual code sends three separate send-keys: (1) `export AGENTRC_PROJECT_ROOT`, (2) `cd worktree`, (3) `agentrc worker heartbeat ... &` as its own command, then (4) `claude --dangerously-skip-permissions '<seed>'` as a final command — no `HB=$!`, no `kill $HB`, no `exit`. When the worker's claude exits, the heartbeat daemon keeps running and the pane stays open. `watch` and `status` therefore report healthy heartbeats for workers that have long since quit, directly undermining the stale-heartbeat signal (`docs/agentrc-implementation-spec.md:482`).
- **Proposed remediation:** Update `spawn.rs` to send the composite bash line (`HB=$! … kill $HB; exit`). Safer than softening the spec because staleness is already used as a health signal by dashboard and resume.
- **Confidence:** high

## F-11: SKILL.md "HARD GATE" claim is not binary-enforced
- **Severity:** high
- **Location:** `skill/agentrc/SKILL.md:51` vs `src/commands/spawn.rs:103-242`
- **Description:** SKILL.md Phase 1 says "HARD GATE: present plan to user. Do NOT spawn workers until user approves." Nothing in `agentrc spawn` verifies a plan has been approved; spawn.rs creates a worktree and launches a worker the moment `run create` has run and a task brief exists. The "hard gate" is pure orchestrator-side social contract. This is acceptable (a deterministic binary can't judge plan approval), but the "HARD GATE" wording misleads readers (including future orchestrators) into thinking the binary enforces it.
- **Proposed remediation:** Soften to "Hard gate (workflow discipline): present plan to user. Do NOT spawn workers until user approves — the binary will not stop you, so self-discipline matters." OR add a check in `spawn` requiring `plan.md` to exist in the active run, populated by the orchestrator only after approval.
- **Confidence:** high

## F-12: "Max 2 redispatches" enforced only by `respawn`/`amend`, not by `integrate`
- **Severity:** high
- **Location:** `skill/agentrc/SKILL.md:103` vs `src/commands/integrate.rs:241-416`
- **Description:** SKILL.md Key Rules: "Max 2 redispatches per task. Then pause and surface to user." Implementation spec (`docs/agentrc-implementation-spec.md:443-453`) says on merge conflict or test failure, integration should redispatch (up to 2 times) or pause. Actual `integrate_in` does NOT redispatch: it records failure in `MergeResult`, aborts the merge, continues to the next task, and returns. No `status.redispatch_count` increment, no `amend`-with-conflict-addendum, no respawn call. The user is expected to read the table and manually redispatch. This is not necessarily wrong (SKILL.md's reactive-integration flow puts the orchestrator in charge), but it contradicts the docs and implementation spec. Redispatch is enforced only in `respawn.rs:40-47` and `amend.rs:58-65`, which simply reject if `redispatch_count >= max_redispatch_attempts`.
- **Proposed remediation:** Update `docs/agentrc-implementation-spec.md:443-453` to match the reactive-orchestrator model — describe `integrate` as a one-shot batch merge that reports and stops, with the orchestrator driving redispatch via `amend` and `respawn`. Also explicitly mention in SKILL.md Phase 3 that `integrate` does not auto-redispatch.
- **Confidence:** high

## F-13: Reader task status has `branch: null`, undocumented in the JSON schema
- **Severity:** high
- **Location:** `docs/agentrc-implementation-spec.md:297-310` vs `src/commands/spawn.rs:142-153, 201-208`, `src/commands/resume.rs:66-79`
- **Description:** Readers correctly skip worktree creation and cd to project root. But the status JSON for a reader will have `branch: null` and no worktree. The schema in the spec shows `branch: "orc/001-add-login-endpoint"` with no hint that readers legitimately have null branches. A user parsing `status --json` programmatically cannot distinguish "reader" from "not yet assigned". The resume output also doesn't identify reader vs writer in its TASK STATUS block. Task `classification` is in the brief but not surfaced in status output.
- **Proposed remediation:** Add `classification` to `TaskStatus` so status rendering (TTY and JSON) can distinguish. Update `docs/agentrc-implementation-spec.md:297-310` to show the null-branch case for readers explicitly.
- **Confidence:** medium

## F-14: Root `CLAUDE.md` and `skill/agentrc/claude-md-section.md` have drifted
- **Severity:** high
- **Location:** `CLAUDE.md:1-42` vs `skill/agentrc/claude-md-section.md:1-45`
- **Description:** These two files are meant to hold the same content (one is the template `agentrc install`/`agentrc init` injects into other projects; the other is this project's injected copy). They have drifted significantly: (1) Root `CLAUDE.md` Worker Contract has a 9th step at line 34 ("NEVER use git push, git rebase…") that the template lacks. (2) Root `CLAUDE.md`'s "Subagent Rules" (lines 37-41) is a terse 2-bullet list. (3) The template has a richer "Git Protocol — STRICT" section with three named subsections: "Worker git allowlist" (lines 38-40), "Subagent git rule" (line 42), and "Orchestrator git rule" (line 44). Neither version is a strict subset of the other. A user running `agentrc init` gets content that differs from what they see in this repo, undermining the template's purpose as a single source of truth.
- **Proposed remediation:** Pick one canonical form — the template's three-section structure is more complete — and propagate it to the root `CLAUDE.md`. Alternatively, add a preface to one of the two files stating "This file is manually maintained; see `skill/agentrc/claude-md-section.md` for the canonical template used by `agentrc init`." Strongly prefer the former. After reconciling, add a test or Make target that diffs them and fails on drift.
- **Confidence:** high

## F-15: README config table omits `heartbeat_interval_sec` and `worker_claude_args`
- **Severity:** high
- **Location:** `README.md:104-115` vs `src/model/config.rs:12-14, 38, 49-50`
- **Description:** `OrchestratorConfig` exports two user-visible fields the README never mentions: `heartbeat_interval_sec` (default 30; controls how often the worker heartbeat daemon touches `.alive`) and `worker_claude_args` (default `[]`; extra args appended to every `claude` invocation the spawn command constructs — e.g. `["--model", "opus"]`). Both are meaningful knobs. `worker_claude_args` in particular is the only supported way to affect the Claude CLI invocation per project; hiding it from the README guarantees users won't discover it. Given the project's own memory-level directive "Always use Opus model" the absence of documentation for `worker_claude_args` is an especially consequential omission.
- **Proposed remediation:** Add two rows to the README Configuration table at `README.md:115`:
  - `` | heartbeat_interval_sec | 30 | How often each worker's heartbeat daemon touches its `.alive` file (seconds) | ``
  - `` | worker_claude_args | [] | Extra args passed to every `claude` worker launch (e.g. `["--model", "opus"]`) | ``
- **Confidence:** high

## F-16: SKILL.md Phase 1 writes `.orchestrator/active/plan.md` before the `active` symlink exists
- **Severity:** high
- **Location:** `skill/agentrc/SKILL.md:46-56` vs `src/commands/run.rs:78-81`
- **Description:** Phase 1 step 6 says "Write plan to `.orchestrator/active/plan.md`." Phase 2 step 1 then says "`agentrc run create --slug <name>`" — which is what creates the `active` symlink. Between Phase 1 and Phase 2 there is no `active/` directory, so the symlink does not exist. A fresh orchestrator session following SKILL.md literally would attempt to write to a path that does not exist. This has probably "worked" in practice because orchestrators commonly run `run create` first, but the directive is still wrong.
- **Proposed remediation:** Reorder Phase 1 / Phase 2 so `run create` happens before the plan is written, or explicitly state the plan is held in memory (as an artifact to show the user) until Phase 2 step 1. Concrete edit at `SKILL.md:52`: "6. Once the user approves, `agentrc run create --slug <name>` and then write the plan to `.orchestrator/active/plan.md`." Shift current Phase 2 step 1 into Phase 1 step 6; Phase 2 starts at "Write task briefs."
- **Confidence:** high

## F-17: README lacks prerequisite-order and install-verification guidance
- **Severity:** high
- **Location:** `README.md:58-73, 116-121`
- **Description:** The Requirements section lists tools but says nothing about installation order or how the four pieces connect. A reader who already has `claude` installed proceeds fine. A reader who does NOT has no idea whether they must install `claude` before `agentrc install`, whether `agentrc install` verifies `claude`, or what the failure mode looks like. `agentrc install` does verify tmux and claude availability (per `docs/agentrc-implementation-spec.md:587-590`), but the README's install story doesn't say so, so readers cannot tell whether `agentrc install` will fail fast or silently skip.
- **Proposed remediation:** Replace the current one-liner at `README.md:60` with: "Requires **Rust** (to build), **tmux**, **git**, and the [**Claude CLI**](https://docs.anthropic.com/en/docs/claude-code) on your `$PATH` before you run `agentrc install`. The install command verifies each prerequisite and exits non-zero if any are missing." Also note near Quick Start that `cargo install --path .` puts `agentrc` on the user's `$PATH` via `~/.cargo/bin/`.
- **Confidence:** high

## F-18: Core terminology (writer/reader, run/task/worker) used without definition
- **Severity:** high
- **Location:** `README.md:56`, `skill/agentrc/SKILL.md:50`, and passim across docs
- **Description:** The terms `writer`/`reader` and `run`/`task`/`worker` are load-bearing but never defined in any user-facing doc. Line 56 of the README says "reader/writer classifications" as if the reader already knows. Classification drives whether `agentrc spawn` creates a worktree (per `docs/agentrc-implementation-spec.md:351-354`). SKILL.md Phase 1 step 4 references "reader/writer classifications" without an introduction — an orchestrator session has no instruction for what these classes *mean*. "Run" is first mentioned in the Quick Reference as `agentrc run create` with no definition. "Bucket" appears in `docs/superpowers/` audit docs without any cross-reference. First-time readers and fresh orchestrator sessions lack a canonical glossary to recover from.
- **Proposed remediation:** Add a short Terminology block in two places. In `README.md` after "How It Works" (around line 56): "A *writer* task modifies code and gets its own `orc/NNN-<slug>` branch + worktree; a *reader* task investigates in read-only mode and shares the project root. A *run* is a named group of related tasks; only one run is active at a time. A *worker* is the Claude Code session spawned for one task." In `skill/agentrc/SKILL.md` after the Quick Reference (around line 43):
  ```markdown
  ## Terminology
  - **writer**: worker task that modifies code; gets branch `orc/NNN-<slug>` and worktree `.orchestrator/active/worktrees/NNN/`.
  - **reader**: worker task that investigates without modifying code; runs in project root; outputs via `agentrc worker note`/`result`.
  - **pane**: tmux pane hosting one Claude Code session.
  - **run**: named set of tasks sharing a plan; one `active` at a time.
  - **integrate**: process of merging completed writer branches in dependency order with test gates.
  ```
  Keep "bucket" out of core docs — that's audit-plan jargon.
- **Confidence:** high

---

## F-19: Undocumented `pane_title` field on `TaskStatus`
- **Severity:** medium
- **Location:** `src/model/task.rs:70`, `src/commands/status.rs:162-166`, `src/commands/resume.rs:69-72` vs `docs/agentrc-implementation-spec.md:297-310`
- **Description:** `TaskStatus` has `pane_title` (populated by spawn/respawn with `orc:<id>:<slug>`), used preferentially over `pane_id` in the TTY status render and resume output. The implementation-spec status JSON example lists `pane_id` but not `pane_title`. JSON consumers treating the spec as authoritative will not expect this field.
- **Proposed remediation:** Add `pane_title` to the spec status JSON example. Document that `pane_title` is the display string while `pane_id` is the tmux identifier.
- **Confidence:** high

## F-20: Undocumented `phase_history` and `token_usage` fields on `TaskStatus`
- **Severity:** medium
- **Location:** `src/model/task.rs:65-84`, `src/commands/worker/status.rs:92-100` vs `docs/agentrc-implementation-spec.md:297-310`
- **Description:** The spec's status JSON schema shows 10 fields; `TaskStatus` has 13 (adds `pane_title`, `phase_history` — array of `{phase, entered_at}` entries, and `token_usage`). `phase_history` is appended on every status update and grows unboundedly over a long-running task. `token_usage` is in `docs/agentrc-phase3-design.md:75-87` but never made it back into the implementation spec. External status consumers (dashboard, user scripts per the README's `--json` promise) see undocumented fields.
- **Proposed remediation:** Update `docs/agentrc-implementation-spec.md:297-310` to include all three fields with example values and types; note `phase_history` is append-only. Consider documenting a phase_history cap.
- **Confidence:** high

## F-21: `watch` and `status` hardcode 120s heartbeat timeout, ignoring `config.heartbeat_timeout_sec`
- **Severity:** medium
- **Location:** `src/commands/watch.rs:14, 105`, `src/commands/status.rs:142` vs `src/model/config.rs:16-18`, `README.md:111`
- **Description:** README says the `heartbeat_timeout_sec` config field controls stale-heartbeat detection (default 120). `watch.rs` declares `const HEARTBEAT_TIMEOUT_SEC: u64 = 120` and uses it directly, ignoring `config.heartbeat_timeout_sec`. `status.rs:142` uses the same hardcoded 120. Users tuning `heartbeat_timeout_sec` in `.orchestrator/config.json` get correct behavior from `resume` (`src/commands/resume.rs:46`) but incorrect behavior from `watch` and `status`.
- **Proposed remediation:** Load config and use `config.heartbeat_timeout_sec` in `watch.rs` and `status.rs::format_tty`. Drop the hardcoded constant.
- **Confidence:** high

## F-22: README and SKILL.md disagree on `teardown` flags
- **Severity:** medium
- **Location:** `README.md:88` vs `skill/agentrc/SKILL.md:36` vs `src/main.rs:39-48`
- **Description:** README says `teardown [task-id] [--all]`. SKILL.md says `teardown <id> [--all] [--force]`. `main.rs:39-48` supports `task_id: Option<String>`, `--all`, and `--force`. README is missing `--force`; SKILL.md has it right. The force flag is behaviorally significant — it bypasses the state check in `src/commands/teardown.rs:37` and lets users tear down in-progress workers.
- **Proposed remediation:** Update README line 88 to `teardown [task-id] [--all] [--force]` and add a sentence: "`--force` bypasses the state check, enabling teardown of `in_progress` workers."
- **Confidence:** high

## F-23: README and SKILL.md both omit `checkpoint list`
- **Severity:** medium
- **Location:** `README.md:89` vs `skill/agentrc/SKILL.md:38-39` vs `src/main.rs:137-155`
- **Description:** README shows `checkpoint save / restore`. SKILL.md shows `checkpoint save [-m "msg"]` and `checkpoint restore [id] [--respawn]`. Actual code has three subcommands: `save`, `list`, `restore`. Both user-facing references omit `list` — the primary way to discover the ID you'd want to restore, a functional discoverability gap.
- **Proposed remediation:** Add `checkpoint list` to both the README Commands table and the SKILL.md Quick Reference.
- **Confidence:** high

## F-24: `agentrc plan` has only one subcommand — consider flattening or defaulting
- **Severity:** medium
- **Location:** `README.md:92`, `src/main.rs:94-98, 117-121`
- **Description:** README says `plan validate`. Implementation has `Plan { subcommand: PlanCommands }` with only `Validate`. `agentrc plan` alone gets a "subcommand required" error. `docs/agentrc-implementation-spec.md:101` positions `plan validate` in Phase 2 scope while the README positions it as Phase 1 standard. Consistent with current implementation, but the spec needs a refresh.
- **Proposed remediation:** Either add `#[command(subcommand_required = false)]` with `validate` as default, or flatten to `agentrc validate`. Also move Phase 2 items out of the "Phasing" tables in the impl spec — they all shipped.
- **Confidence:** medium

## F-25: Impl spec still labeled "Draft, pending user review"; Phase 2 section out of date
- **Severity:** medium
- **Location:** `docs/agentrc-implementation-spec.md:3-4, 98-107`
- **Description:** Header says `**Status:** Draft, pending user review` but the implementation has clearly landed (binary exists, Phase 1 and Phase 3 plans reference it as done, git history shows merged implementation branches). Phase 2 section says "Additions to the same binary: `agentrc plan validate`, Smarter integration, `agentrc amend <task-id> --from-brief`, `notify`-based filesystem watching, Richer status reporting with estimated completion times." These are all shipped, except `amend` uses `--brief <file>` and `--message <text>` rather than the spec's `--from-brief`. Readers cannot tell whether this is current spec or a draft being revised.
- **Proposed remediation:** Change status to `**Status:** Implemented (Phase 1, Phase 2, Phase 3 complete). Living reference for core workflow semantics.` Append a short "Deviations from spec" section noting where implementation diverged (`events` command added later; `amend --brief` not `--from-brief`; etc.). Restructure `docs/agentrc-implementation-spec.md:70-107` as a historical phase-progression narrative, or delete the phasing section entirely.
- **Confidence:** high

## F-26: `docs/tmux-workflow-design-spec.md` not marked as superseded
- **Severity:** medium
- **Location:** `docs/tmux-workflow-design-spec.md:1-10, 5, 24, 32, 34, 44-51, 73-82`
- **Description:** This is the original design doc under the old project name `tmux-teams`. `docs/agentrc-implementation-spec.md:5` correctly identifies it as "Supersedes" — but the superseded doc itself carries no such marker. A reader opening `tmux-workflow-design-spec.md` directly (Google result, stale link, `docs/` listing) has no indication the contents are historical and the project has been renamed. Every reference to `tmux-teams` (command names, skill paths, binary name) in this file is stale.
- **Proposed remediation:** Add a prominent header at `docs/tmux-workflow-design-spec.md:1`:
  ```markdown
  # tmux-teams — Design Spec (HISTORICAL)
  **Status:** superseded by `docs/agentrc-implementation-spec.md` on 2026-04-11.
  **Project renamed:** tmux-teams → agentrc. Every `tmux-teams` reference below is historical; the current binary name is `agentrc`.
  ```
  Or move the file to `docs/archive/`.
- **Confidence:** high

## F-27: `docs/agentrc-phase1-plan.md` and `docs/agentrc-phase3-plan.md` lack status markers
- **Severity:** medium
- **Location:** `docs/agentrc-phase1-plan.md:1-11`, `docs/agentrc-phase3-plan.md:1-11`
- **Description:** These are detailed implementation plans with `- [ ]` checkboxes. Neither has a `Status:` header. A reader cannot tell whether the checkboxes are to-do items, a historical artifact, or a living instruction set. The repo's git history shows the described work has landed.
- **Proposed remediation:** Add a status header at the top of both plans:
  ```markdown
  **Status:** Implemented (historical). Retained for the line-by-line TDD recipe.
  **Do not follow the `- [ ]` steps to drive new work.** Implementation has moved past these plans; see `src/` for the current code.
  ```
- **Confidence:** high

## F-28: `docs/agentrc-phase3-design.md` lacks a status marker
- **Severity:** medium
- **Location:** `docs/agentrc-phase3-design.md:1-3`
- **Description:** Unlike `agentrc-implementation-spec.md`, Phase 3 design has no front-matter header. It reads as current spec, and some of it is (checkpoint schema, detect module). Other parts have evolved (dashboard key bindings at lines 176-189 should be cross-checked against `src/tui/`). Readers cannot tell which parts are current.
- **Proposed remediation:** Add a status block mirroring `agentrc-implementation-spec.md`:
  ```markdown
  **Status:** Implemented. Source of truth for dashboard/checkpoint/respawn semantics.
  **Last verified against code:** <date or commit hash>
  ```
- **Confidence:** medium

## F-29: `docs/ascii-animations-design.md` has no status, date, or module-location marker
- **Severity:** medium
- **Location:** `docs/ascii-animations-design.md:1-4`
- **Description:** Opens with `# ASCII Animations for Dashboard` and `## Overview` with no date, author, status, or module pointer. Reader cannot tell if it was implemented, is a proposal, or is future work. Module paths referenced (`src/tui/anim/`) should be verified against the codebase.
- **Proposed remediation:** Add a 3-line header:
  ```markdown
  **Date:** <YYYY-MM-DD>
  **Status:** <Implemented | Proposal | Superseded by X>
  **Module location:** `src/tui/anim/`
  ```
- **Confidence:** medium

## F-30: SKILL.md Bootstrap runs `agentrc dashboard` before any run exists
- **Severity:** medium
- **Location:** `skill/agentrc/SKILL.md:16-21` vs `src/commands/dashboard.rs:20-22`
- **Description:** SKILL.md Bootstrap: "Launch the dashboard in a side pane: `tmux split-window -h -l 45% 'agentrc dashboard'`." Bootstrap happens on skill activation — the FIRST thing in a session — before the orchestrator has created a run. `agentrc dashboard` likely errors on `AppError::NoActiveRun` and renders empty/error until `run create`. Not broken per se, but jarring: the skill auto-launches a dashboard into a black hole, and the dashboard doesn't auto-refresh to pick up the newly-created run until user interaction.
- **Proposed remediation:** Teach the dashboard to render "No active run — waiting for `agentrc run create`" and poll for run creation so it comes alive automatically. Or move the `tmux split-window` to Phase 2 (DISPATCH) in SKILL.md, after `run create`.
- **Confidence:** medium

## F-31: README "Branches that skip tests get redispatched" isn't wired to `integrate`
- **Severity:** medium
- **Location:** `README.md:8` vs `src/commands/integrate.rs:241-416`, `src/commands/audit.rs`
- **Description:** README bullet: "TDD enforced — red-green-refactor is a workflow invariant, not a suggestion. Commit history is audited at integration. Branches that skip tests get redispatched." Actual `integrate_in` does not audit TDD, does not check commit messages, and does not redispatch on TDD violation. `agentrc audit <task-id>` exists separately but must be invoked manually, and its result does not feed into `integrate`. A user trusting the README will be surprised when `integrate` happily merges a branch with zero `test:` commits.
- **Proposed remediation:** Wire `audit::audit_tdd` into `integrate_in` as a pre-merge check (with a `--skip-audit` escape hatch), or soften the README: "Commit history can be audited with `agentrc audit <task-id>` and surfaced to the orchestrator for TDD judgement."
- **Confidence:** high

## F-32: README lacks a troubleshooting / known-issues section
- **Severity:** medium
- **Location:** `README.md` (entire file)
- **Description:** The system has many moving parts: tmux, git worktrees, Claude CLI, heartbeats, skill symlinks. Common failure modes (broken skill symlink; dirty base branch; `claude` not on $PATH; tmux not running; manually-killed worker pane; orphaned `active` symlink; tests failing on base branch; `runs/` directory growth) are predictable and worth documenting. None are. A user hitting any gets the binary's terse error message and no next step.
- **Proposed remediation:** Add `## Troubleshooting` to the README, or better, `docs/troubleshooting.md` linked from README. Seed with 6–10 common failures and their fixes (re-run `agentrc install` for broken symlink; `git status` clean required before `spawn`; `claude --version` for PATH check; stale tmux session; `agentrc run archive` then `run create` for orphaned `active`; fix base-branch tests before `integrate`; manual cleanup of old `runs/*`).
- **Confidence:** high

## F-33: Worker subcommands get one sentence in README; no flag reference user-visible
- **Severity:** medium
- **Location:** `README.md:96` vs `src/main.rs:158-216`
- **Description:** "Workers use `agentrc worker *` subcommands internally for status reporting, heartbeats, notes, and completion signaling." — the README's full coverage. Workers are Claude Code sessions, but humans reading the docs need enough shape to (a) understand what the worker prompt tells them to do, (b) debug a worker misusing a command, (c) write task briefs that reference them correctly. The full subcommand list with flags exists only in source and `docs/agentrc-implementation-spec.md:131-141` (which is missing `--phase` / `--tokens` flags on `worker status` per `src/main.rs:168-175`).
- **Proposed remediation:** Add a subsection `### Worker subcommands (used inside spawned worker sessions)` to the README after the commands table, listing each of the 5 worker commands with their flags. Or create `docs/worker-commands.md` and link from README. Keep the list in sync with `src/main.rs` via `clap`'s help output.
- **Confidence:** high

## F-34: `worker-seed.txt` and `CLAUDE.md` reference external skills (`superpowers:*`, `voltagent-*`) with no install pointer
- **Severity:** medium
- **Location:** `skill/agentrc/worker-seed.txt:7`, `CLAUDE.md:8-17`, README (absent)
- **Description:** Worker step 4 in `worker-seed.txt` reads: "For writer tasks: invoke `superpowers:test-driven-development` and follow TDD rigorously." `CLAUDE.md` references `voltagent-lang:rust-engineer`, `voltagent-qa-sec:test-automator`, etc. These are external Claude Code skill bundles the user may not have installed. No README pointer, no check during `agentrc install`, no graceful degradation.
- **Proposed remediation:** (a) Add an "Ecosystem" or "Assumed skills" section to the README noting that agentrc assumes `superpowers` and `voltagent-*` skill bundles are installed, with install pointers. (b) Extend `agentrc install` to warn if the referenced skill namespaces are absent from `~/.claude/skills/`. (c) Soften the worker seed: "follow TDD rigorously (if `superpowers:test-driven-development` is installed, invoke it; otherwise do red → green → refactor manually)."
- **Confidence:** high

## F-35: `task-brief.md` template placeholders are undocumented
- **Severity:** medium
- **Location:** `skill/agentrc/task-brief.md:1-29`
- **Description:** The template uses `{{ID}}`, `{{SLUG}}`, `{{CLASSIFICATION}}`, `{{WORKTREE}}`, `{{BASE_BRANCH}}`, `{{BRANCH}}`, `{{DEPENDS_ON}}`, `{{CREATED_AT}}`, `{{TITLE}}`, `{{SCOPE}}`, `{{TEST_PLAN}}`, `{{ACCEPTANCE_CRITERIA}}`, `{{OUT_OF_SCOPE}}`, `{{NOTES}}`. Nothing documents (a) required vs optional, (b) valid values (e.g., `CLASSIFICATION` must be `writer` or `reader`), (c) the format of `DEPENDS_ON` (comma-separated? YAML list? quoted?), or (d) who substitutes them (the orchestrator, by hand).
- **Proposed remediation:** Add a comment block above the frontmatter documenting each placeholder with type and required/optional status; or move to `docs/task-brief-reference.md` linked from the template.
- **Confidence:** high

## F-36: No LICENSE file despite README claiming MIT
- **Severity:** medium
- **Location:** `README.md:123-125`, repo root (no LICENSE file)
- **Description:** README says "## License\n\nMIT" but there's no `LICENSE`, `LICENSE.md`, or `LICENSE.txt` at the repo root. GitHub cannot auto-detect the license without a standard file, users cannot legally rely on the README claim alone in many jurisdictions, and this is commonly required for `cargo publish` and corporate/legal review.
- **Proposed remediation:** Add a `LICENSE` file at the repo root with standard MIT license text (copyright line "Copyright (c) 2026 Eric Smith"). No README change needed.
- **Confidence:** high

---

## F-37: README `integrate [--dry-run]` doesn't mention what dry-run outputs
- **Severity:** low
- **Location:** `README.md:86` vs `src/commands/integrate.rs:128-163`
- **Description:** README says `integrate [--dry-run]` "Merge branches in dependency order with test gates." `--dry-run` produces markedly different output (would-merge task list, per-task changed files, overlap detection across tasks) that users won't realize without running it. A one-sentence addition would help.
- **Proposed remediation:** `integrate [--dry-run]` / "Merge writer branches in dependency order with test gates; `--dry-run` previews the merge plan and flags files touched by multiple tasks."
- **Confidence:** medium

## F-38: `layout [tile|collate]` behavior undocumented in impl spec
- **Severity:** low
- **Location:** `README.md:94` vs `docs/agentrc-implementation-spec.md:83, 119` vs `src/commands/layout.rs:110-163`
- **Description:** README lists `layout [tile|collate]`. Implementation has a solid collate algorithm that redistributes panes into `workers-2`, `workers-3`, etc. windows respecting `workers_per_window`. The spec mentions collate only once (line 83) as "collate overflow to new windows" without explaining output. Users don't know what `collate` does without running it.
- **Proposed remediation:** Expand the README row: `` | layout [tile\|collate] | Retile worker panes; `collate` splits excess panes into `workers-2`, `workers-3`, etc., respecting `workers_per_window` | ``.
- **Confidence:** medium

## F-39: No CONTRIBUTING.md or CHANGELOG.md
- **Severity:** low
- **Location:** repo root (absent)
- **Description:** No CONTRIBUTING.md (build/test/run/PR flow) or CHANGELOG.md (version history). The Makefile (`make test | make smoke | make install` per `docs/agentrc-implementation-spec.md:151`) is not referenced from any user-facing doc. Not urgent for a solo project but expected once it attracts external contributors.
- **Proposed remediation:** Defer until first release tag. When added: CONTRIBUTING.md covers `cargo build`, `cargo test`, `make smoke`, TDD expectations, and the agentrc worker protocol for self-hosted development. CHANGELOG.md follows Keep-a-Changelog.
- **Confidence:** medium

## F-40: README Commands table mixes syntax conventions
- **Severity:** low
- **Location:** `README.md:77-95`, `skill/agentrc/SKILL.md:28-43`
- **Description:** The table uses `<required>`, `[optional]`, `|` for alternation (`tile\|collate`), and prose-only for `worker *`. Additionally `checkpoint save / restore` (line 89) uses a slash convention that appears nowhere else; `run create / list / archive` (line 93) repeats it. Minor scan-ability cost.
- **Proposed remediation:** Normalize to one convention — e.g., `|` for alternation (`checkpoint save|restore|list`, `run create|list|archive`), `<required>`/`[optional]` for arguments/flags. Apply uniformly to README:77-95 and SKILL.md:28-43.
- **Confidence:** medium

## F-41: "integrate" vs "merge" verb usage is minorly inconsistent
- **Severity:** low
- **Location:** `README.md:13, 56, 86`; `docs/agentrc-implementation-spec.md:84, 120, 437`
- **Description:** README line 13: "Merges happen in dependency order"; line 56: "Branches merge in dependency order"; command description at 86: "Merge branches in dependency order with test gates". The command is named `integrate`, the phase is `INTEGRATE`, and `merge` is the underlying git op. Consistent upon close reading, but toggles freely in the same surface area.
- **Proposed remediation:** Add a one-sentence gloss to the README: "*Integrate* is the process (resolve deps, run tests, merge, review); *merge* is the underlying git op `integrate` performs." Or pick `integrate` as canonical for the process-level verb.
- **Confidence:** medium

## F-42: README's second "Architecture" paragraph is redundant with the diagram + "How It Works"
- **Severity:** low
- **Location:** `README.md:98-100`
- **Description:** Reader flow: intro bullets → architecture diagram → How It Works → Quick Start → Commands → Architecture (again, prose). The second Architecture section re-explains the two-layer model the ASCII diagram and "How It Works" have already covered. A top-to-bottom reader encounters the abstract model three times.
- **Proposed remediation:** Delete the second Architecture section and inline its one load-bearing sentence ("The LLM decides *what*. The binary handles *how*.") into "How It Works." Alternatively, promote the second Architecture section above the Commands table.
- **Confidence:** medium

## F-43: Tiny typos and style drifts across docs
- **Severity:** low
- **Location:** multiple
- **Description:**
  - `README.md:15` "Tmux-native" — other docs and the diagram use lowercase `tmux` (upstream's own style).
  - `README.md:7, 8` uses `--` (double hyphen) where typographic em-dashes (`—`) match the rest of the document (e.g., `README.md:20, 100`).
  - Mixed em-dash vs ASCII hyphen between adjacent tables in different files — pick one and sweep.
  - `skill/agentrc/SKILL.md:38-40` uses `checkpoint save [-m "msg"]` while `docs/agentrc-phase3-design.md:222` uses `-m "description"`. Prefer `-m "<description>"` for clap-style consistency.
- **Proposed remediation:** One style-sweep pass: standardize on em-dashes, lowercase `tmux`, and one angle-bracket convention for placeholders. Low priority unless already editing the files.
- **Confidence:** medium

---

## Clean Areas (no findings)

- **README ASCII architecture diagram** (`README.md:27-50`) — accurate, matches current docs, correct binary name throughout.
- **Image paths** — `docs/images/dashboard.png` and `docs/images/workers.png` both exist (verified). No broken image references.
- **Internal Markdown links** — only `README.md:100 → skill/agentrc/SKILL.md` checked; resolves correctly.
- **GitHub URL consistency** — `https://github.com/ericsmithhh/agent-rc` identical across `README.md:63`, `CLAUDE.md:4`, and `skill/agentrc/claude-md-section.md:4`.
- **Worker-seed git-allowlist section** — `skill/agentrc/worker-seed.txt:15-23` matches SKILL.md Git Protocol (both allow `git add/commit/status/diff/log` and forbid the same set). The drift is between root `CLAUDE.md` and `claude-md-section.md` only — see F-14.
- **`run create/list/archive`** — `src/commands/run.rs:51-129` matches `docs/agentrc-implementation-spec.md:123-129` and SKILL.md:32-33.
- **`worker status/note/result/done/heartbeat`** — all five present in `src/commands/worker/` with flag surfaces matching `docs/agentrc-implementation-spec.md:131-141`.
- **`plan validate` logic** — `src/commands/plan.rs:40-135` matches the documented behavior.
- **`checkpoint save/restore` schemas** — `src/commands/checkpoint.rs:16-37` closely matches `docs/agentrc-phase3-design.md:229-251` (minor `pane_alive: bool` addition is acknowledged in a clear code comment).
- **`worker`, `pane`, `reader`/`writer` terminology usage within code** — once introduced (see F-18 for the introduction gap), usage is consistent across README, SKILL.md, worker-seed.txt, and src/commands/.
