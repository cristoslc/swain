# Changelog

## [0.12.0-alpha] - 2026-03-21

### Features

#### Contract-driven changelog pipeline

The changelog generation pipeline is now governed by a data contract (changelog-contract.yaml) that defines per-field interpretation rules instead of scattering them across SKILL.md prose. Each field has a semantic (what it means), source (where data comes from), and quality block (rules, anti-patterns with explanations, good/bad examples). The agent reads the contract before classifying commits, producing better-structured data for the Jinja2 template to render.
- "Coming Next" section replaces "Roadmap" in changelogs — forward-looking previews of planned work instead of artifact state transitions

### Research
- Data contract standards — surveyed ODCS v3.1.0, datacontract.com spec v0.9.0, and OpenMetadata Data Contract entity to inform ADR-014

## [0.11.0-alpha] - 2026-03-21

### Features

#### Auto-detecting trunk branch

swain-trunk.sh detects the development branch from git worktree state instead of hardcoding it. Repos on develop, main, trunk, or any branch are supported automatically with zero configuration. All runtime skills (swain-sync, swain-doctor, swain-release) now use dynamic detection via a $TRUNK variable sourced at workflow start. An optional git.trunk override in swain.settings.json handles edge cases like detached HEAD, but is never required for normal operation.
- Doctor and preflight now detect whether the trunk+release model is configured and advise on migration

### Coming Next
- Data contracts for agent-produced data — a lightweight schema+semantics+quality contract format that gives agents scoped per-field interpretation rules instead of unstructured prose. The changelog pipeline is the first consumer; future skills will follow the same pattern.

### Supporting Changes
- Jinja2 changelog template with H4 feature headings for swain-release
- Changelog pipeline rewritten to be contract-driven — interpretation rules now live in changelog-contract.yaml instead of SKILL.md prose
- v0.10.0-alpha release retrospective

## [0.10.0-alpha] - 2026-03-21

### Features

**CLI roadmap renderer** — `chart.sh roadmap --cli` produces deterministic, terminal-friendly output grouped by Eisenhower quadrant with all first-degree children (EPICs, SPECs, SPIKEs) nested equally under their parent initiative. New `swain-roadmap` skill wraps it as the user-facing entry point: regenerate ROADMAP.md, open it, and display a scannable CLI summary.

### Roadmap

- VISION-004 (Operator Cognitive Support), INITIATIVE-019 (Session-Scoped Decision Support), EPIC-039 (Session Facilitation Rebuild), and 6 supporting SPECs (118–123) covering session lifecycle, roadmap decisions, detection hooks, and skill alignment
- SPEC-116 (Read Before Reasoning), SPEC-117 (Evidence Basis For All Actions) — retro learnings from SPIKE-022 to SPEC-114 session

### Research

- Google Stitch SDK trove — 7 sources collected and normalized across 2 research sessions

### Supporting Changes

- iTerm tab name bleed fix — OSC title escapes now target the specific client terminal instead of using global `tmux set-titles` (SPEC-124)
- Artifact cross-reference enrichment — ~100 doc files now have sorted, bidirectional `linked-artifacts` frontmatter
- SPEC-114 (Worktree Landing via Merge with Retry) completed and verified
- swain-release changelog format now uses four fixed sections: Features, Roadmap, Research, Supporting Changes

## [0.9.0-alpha] - 2026-03-20

### Trunk+Release Branch Model

swain now supports a two-branch workflow where `trunk` is the development
branch and `release` is squash-merged at release time. A migration script
handles the rename from `main` to `trunk`, and all skill references have been
updated. "Merge-With-Retry Replaces Rebase-Then-Push" (ADR-011) replaces the
fragile rebase-then-push strategy with a merge-with-retry loop for worktree
landing, and "Trunk+Release Branch Model" (ADR-013) codifies the two-branch
convention.

### Roadmap: Level-Based Initiative Children

SPECs and Spikes attached directly to an Initiative (without an Epic wrapper)
now appear as first-class items in ROADMAP.md — visible in Eisenhower tables,
Gantt charts, and progress counters. Previously, only Epics were rendered;
direct-child specs were silently dropped. The filtering is now level-based
(any 1-deep child of an Initiative) rather than type-based.
("Roadmap Initiative children use level-based filtering, not type-based" —
SPEC-115)

### Supporting Changes

- Expanded domain field guidance in DESIGN artifact template — documents valid
  `domain` enum values (`interaction`, `data`, `system`)
- Quadrant boundary alignment and X-axis jitter fix for roadmap scatter plot
- Dependency graph now uses `flowchart TD` layout
- Link corrections and ROADMAP regeneration

## [0.8.0-alpha] - 2026-03-20

### Security Scanning (EPIC-017, EPIC-023)

Swain now has a built-in security posture — not just "run a scanner" but a
layered system that integrates into the existing workflow at multiple points.

**swain-security-check** — a new skill that orchestrates gitleaks, osv-scanner,
trivy, semgrep, and two built-in scanners (context file injection, threat surface
heuristic) into a unified, severity-bucketed report. Missing scanners are skipped
with install hints — the scan always completes. (SPEC-058, SPEC-060, SPEC-062)

**Doctor integration** — swain-doctor now checks scanner availability on session
start, so the operator knows what coverage they have before they need it.
(SPEC-059, SPEC-061)

**Workflow gates** — a post-implementation security gate runs automatically before
claiming work is complete, and a pre-claim security briefing summarizes findings
inline. External security skills can hook in via a documented interface.
(SPEC-063, SPEC-064, SPEC-065)

**Validation** — RUNBOOK-001 documents the end-to-end security epics test plan,
first run 25/25 PASS.

### Docker Sandbox (swain-box)

swain-box grew from a proof-of-concept Docker wrapper into a real launcher with
multi-step UX.

**Unified two-step flow** — the launcher now walks through authentication first
(OAuth token from Keychain, API key detection, login confirmation), then
isolation (worktree-enforced sandbox with bind-mounted project files). Auth and
isolation are separate menus, not a single flag soup. (SPEC-081, SPEC-092)

**Credential handling** — a long tail of OAuth and API key bugs resolved:
Keychain JSON extraction, config mounting, env cleanup, tilde expansion,
apiKeyHelper injection, and the `--` separator for agent args. The launcher
now warns clearly when credentials are missing rather than failing silently.

**Planning** — EPIC-030 (multi-agent runtime), VISION-002 (Safe Autonomy), and
capability bridge artifacts lay the groundwork for the next phase of sandbox
work.

### TRAIN Artifact Type (SPEC-091)

A new artifact type for training materials, documentation guides, and onboarding
content. TRAIN gets the full lifecycle treatment: type definition, Jinja2
template, staleness detector (`train-check.sh`), inference routing, specwatch
integration, phase transition hooks, and frontmatter parser support.

As part of this work, "enriched linked-artifacts" were renamed to the clearer
**artifact-refs**, and a new **sourcecode-refs** field was added for linking
artifacts to implementation files. (SPEC-094)

### Design Integrity (EPIC-035)

Artifacts can now detect when their own content has drifted from what was
reviewed and approved.

**design-check.sh** — compares blob SHAs of design-critical sections against
stamped baselines, surfacing drift in specwatch, swain-sync, and swain-design
workflows. (SPEC-096, SPEC-097)

**Design Intent** — DESIGN artifacts gain a new section for capturing the
original design rationale, making it easier to judge whether a drift is
intentional evolution or accidental decay. (SPEC-095)

**Overlap detection** — swain-design now scans active same-type artifacts for
scope overlap when creating new DESIGN, Persona, or Runbook artifacts,
preventing duplicate or conflicting standing-track work.

### Strategic Planning

- Add VISION-002 (Safe Autonomy) and VISION-003 (Swain Everywhere) with
  portability initiative and research spikes
- Add INITIATIVE-017 for unattended agent safety guardrails (EPIC-037, SPIKE-037)
- Consolidate initiative hierarchy and add session atomization epic
- Complete INITIATIVE-011 + INITIATIVE-012 (credential scoping, multi-runtime)
- Add INIT-009 Unified Project State Graph with 4 child EPICs
- Add ADR-007 Event-Driven Orchestrator Replaces Prose Chaining Table

### Research
- Design staleness and drift detection trove (7 sources)
- Docker sandboxes and docker-agent troves
- Claude Code plugins intercom trove
- SPIKE-028/029/030 portability findings

### Supporting Changes
- Gracefully handle unauthenticated gh CLI in swain-keys
- Fix rebuild-index spike type mapping to docs/research/
- Slim AGENTS.md from 220 to ~60 lines, remove deprecated artifact types
- Add decision protection as core swain concept
- Skill audit remediation (EPIC-031)
- Add MCP Server specs (SPEC-082–091) for EPIC-033
- swain-do: pre-plan implementation detection and retroactive-close (#72)
- swain-do: fix ticket title extraction (#66), stale path resolution (#71),
  table parser pipe artifacts (#74), bookmark non-interactivity (#64)
- Release claim lock on close to prevent stale lock accumulation (tk)

## [0.7.0-alpha] - 2026-03-17

### New Features
- Pane-aware tmux tab naming with `--path` flag and worktree support (SPEC-056)
- SPEC-054 Project Identity Enforcement

### Research
- SPIKE-025 Authentication for Public Intake Channels — threat model, TOTP-in-the-clear assessment, auth mechanism evaluation, synthesis, integration sketch, and spike completion

### Bug Fixes
- Use `set +e` in tab-naming script to prevent session-start failures
- Rewrite TOTP analysis to center on replayability (SPIKE-025)
- Close cross-reference gaps across 79 artifact files

### Other Changes
- Add THIRD_PARTY_NOTICES for vendored tk (MIT, wedow/ticket)
- Add attribution header to `skills/swain-do/bin/tk`
- Add acceptance test suite for tab naming
- Refactor `swain-tab-name.sh`: extract `resolve_path()`, per-window hooks, `SWAIN_TMUX_SOCKET` override for testability

## [0.6.0-alpha] - 2026-03-16

### Trove Redesign (BREAKING)

"Evidence pool" is now "trove" — a better name for what swain-search produces,
which ranges from research evidence to reference libraries to repo mirrors.
`evidencewatch` becomes `trovewatch`.

**Hierarchical sources** — sources are no longer flattened to `001-slug.md`. Each
source gets its own directory (`sources/<source-id>/`), and repository or
documentation-site sources mirror their original tree structure. Large sources can
be selectively ingested (`selective: true`).

**Migration** — `migrate-to-troves.sh` converts existing evidence pools
non-destructively. `swain-doctor` detects unmigrated pools and offers migration.

**Wordlist disambiguator** — when source-id slugs collide within a trove, a
`__word1-word2` suffix is appended from a curated wordlist.

### Swain Chart & Specgraph

- Add `swain chart` CLI with lens framework and VisionTree renderer
- Extend priority-weight cascade to epics
- Wire swain chart into all skill invocations

## [0.5.0-alpha] - 2026-03-15

### Prioritization Layer

Swain now answers "what matters most?" — not just "what's actionable?"

**Initiative artifact type** — a new layer between Vision and Epic for grouping
related work under a strategic focus. Epics and standalone specs attach to
Initiatives; Initiatives attach to Visions. This gives the operator a way to
say "security matters more than polish right now" and have swain's
recommendations follow.

**Vision-weighted recommendations** — Visions carry a `priority-weight`
(high/medium/low) that cascades through the hierarchy. The recommendation
formula (`score = unblock_count × vision_weight`) surfaces decisions with the
most downstream leverage in the highest-priority strategic direction.

**Attention tracking** — swain scans git history to show where the operator has
actually been spending time vs. where they said they'd focus. Drift alerts fire
when a high-priority vision goes untouched past a configurable threshold.

**Focus lane** — the operator can say "focus on security" to scope
recommendations to a single vision or initiative. Other lanes appear as
peripheral awareness ("Meanwhile: Design has 4 pending decisions") — visible
but not nagging.

**Guided migration** — `swain-doctor` detects existing epics without an
Initiative parent and walks the operator through grouping them, creating
Initiatives, and setting vision weights. Migration is incremental — one vision
at a time.

### Supporting Changes

- Three new specgraph commands: `recommend`, `decision-debt`, `attention`
- Mode inference in swain-status (vision mode vs detail mode, with ask on ambiguity)
- Artifact type selection guide in swain-design (Initiative vs Epic vs Spec)
- Metadata update workflow for `priority-weight` and `parent-initiative`
- Prioritization settings in `swain.settings.json` (drift thresholds, attention window)
- Updated all reference docs: relationship model, lifecycle tracks, specgraph guide, phase transitions, quick-ref

## [0.4.0-alpha] - 2026-03-14

### Changes
- Rewrite README to focus on decision traceability and human-AI alignment
- Add alpha status callout
- Remove experimental sandbox section
- Remove deprecated swain-push from skills table
- Adopt 0.x semver to reflect alpha status (previous v1/v2/v3 tags preserved as history)

## [3.0.0] - 2026-03-14

### Breaking Changes
- **swain-do now requires worktree isolation for implementation work.** When invoked from the main worktree for plan creation, task claim, or code execution, swain-do invokes the `using-git-worktrees` superpowers skill to create a linked worktree first. If superpowers is not installed, swain-do stops and reports rather than running in the main worktree. Read-only operations (`tk ready`, status checks) are unaffected.

### New Features
- **Isolated execution (`claude-sandbox`)** — new `scripts/claude-sandbox` launcher runs Claude Code inside a sandboxed environment. Tier 1 uses native OS sandboxing (macOS `sandbox-exec`, Linux Landlock/bubblewrap). Tier 2 (`--docker`) runs in a Docker container with bind-mounted project files. Config via `swain.settings.json` (`sandbox.dockerImage`, `sandbox.allowedDomains`). (EPIC-005, SPEC-048, SPEC-049)
- **Specgraph Python rewrite** — `specgraph.sh` replaced by a Python implementation with a full CLI: `build`, `ready`, `next`, `status`, `overview`, `mermaid`, `blocks`, `blocked-by`, `tree`, `neighbors`, `scope`, `impact`, `edges`. Finished artifacts hidden by default; `--all` shows them. (EPIC-013, SPEC-030/031)
- **Cross-reference (xref) validation** — specgraph now validates bidirectional frontmatter consistency across all artifacts. Body references not declared in frontmatter and missing reciprocal links are surfaced in `swain-status` as a Cross-Reference Gaps section. (SPEC-032, SPEC-033)
- **Automatic worktree lifecycle** — swain-sync is worktree-aware: detects linked worktree context, rebases onto `origin/main` when no upstream exists, pushes via `HEAD:main`, opens a PR on branch-protection rejection, and prunes the worktree after landing. swain-doctor detects stale linked worktrees (orphaned, merged, unmerged) and reports cleanup commands. (EPIC-015, SPEC-039, SPEC-043, SPEC-044, ADR-005)
- **swain-status decision support** — status output now leads with a single ranked Recommendation (highest-unblock-count ready item), followed by a Decisions Needed table for human-gated artifacts. (SPEC-036)
- **Artifact workflow efficiency** — fast-path authoring skips full lifecycle ceremony for low-ceremony artifacts. Lazy index rebuild defers specgraph cache updates until needed. Inline lifecycle hash stamping collapses stamp commits into their transition commit. (EPIC-014, SPEC-045/046/047)
- **MOTD improvements** — staged/unstaged/untracked file counts in the header. Interactive Commit & Push button. Reactive agent status updates via Claude Code hooks (no manual `motd update` required). Border animation direction fixed. (EPIC-011, SPEC-040/041/042)
- **Dynamic track resolution** — specgraph now reads the `track` field from artifact frontmatter to classify resolution logic, replacing the hardcoded `RESOLVED_RE` regex. Existing artifacts backfilled with `track` values. (SPEC-038)
- **Model routing annotations** — all skills annotated with `<!-- swain-model-hint: {model}, effort: {level} -->` for runtime model selection. (EPIC-007, SPEC-026)
- **Agent dispatch** — `swain-dispatch` ships artifacts to background agents via GitHub Issues + Claude Code Action workflow. (EPIC-010)
- **Automated retrospectives** — `swain-retro` captures learnings at EPIC completion or on demand, prompts reflection questions, and distills findings into memory files. (SPEC-011)

### Fixes
- Fix `ticket-query` crash with `TICKETS_DIR: unbound variable` when called by external scripts (SPEC-035)
- Fix specgraph `ready` command leaking standing-track artifacts (ADR, PERSONA, JOURNEY, VISION, RUNBOOK, DESIGN) into implementation-ready list (SPEC-037)
- Fix swain-doctor to auto-create `swain.settings.json` when missing
- Fix specwatch to suppress superseded-ADR warnings for closed artifacts
- Fix swain-session to store `session.json` per-project in `.agents/` instead of global memory (SPEC-027)
- Fix `.worktrees/` not gitignored — added pattern to `.gitignore`

### Documentation
- README: add Isolated execution section (`claude-sandbox` usage)
- README: document automatic worktree isolation in swain-do and swain-sync workflow
- ADR-005: document worktree lifecycle decision — swain-do creates, swain-sync lands

## [2.0.0] - 2026-03-12

### New Features
- Add swain-session and swain-stage skills (tmux workspace, bookmarks, preferences)
- Add swain-status skill for cross-cutting project dashboard
- Add swain-help skill for contextual help and onboarding
- Add swain-init skill for one-time project onboarding
- Add swain-keys skill for per-project SSH key provisioning
- Add swain-search evidence pool collection and normalization (EPIC-001)
- Add specgraph dependency visualization with hide-finished default
- Add specwatch bd-sync checker and two-phase audit workflow
- Add swain meta-router for sub-skill dispatch
- Add OSC 8 clickable hyperlinks for artifact IDs
- Add decision-support rendering with impact sorting to swain-status
- Add verification gate for Spec Testing phase
- Add Textual TUI MOTD for swain-stage
- Backup local modifications before skill update

### Fixes
- Fix doctor/update: add command-based detection alongside HOME dotfolder checks
- Fix update: autodetect agent platforms to prevent dotfolder clutter
- Fix doctor: clean up platform dotfolders created by npx skills add
- Fix doctor: clean up retired pre-swain skills during legacy cleanup
- Fix swain-session: use #W format token for tmux set-titles-string
- Fix specwatch: grep -c zero-match fallback
- Fix swain-stage: redesign focus layout as 3-pane with browser and TUI MOTD

### Documentation
- Frame swain around operator decision-support and agent alignment
- Rewrite README for new user onboarding (EPIC-003)
- Create VISION-001, PERSONA-001/002, JOURNEY-001/002, EPIC-002/003/004
- Complete SPIKE-003/004, close SPIKE-001/002
- Add EPIC-004 + SPIKE-004: Superpowers integration assessment
- Unify BUG into SPEC type system

### Refactoring
- Centralize session bookmark updates via swain-bookmark.sh
- Extract reference docs and restructure swain-design SKILL.md
- Extract governance content into single-source-of-truth reference file
- Slim AGENTS.md and relocate detail into skill files
- Migrate python3 invocations to uv run
- Remove automated conflict resolution from swain-push

## [1.1.0] - 2026-03-10

### Breaking Changes
- Rename swain-config → swain-doctor (legacy cleanup handles the transition)

### New Features
- Add beads gitignore hygiene to swain-doctor — validates `.beads/.gitignore` against canonical reference every session, patches missing entries
- Add `git rm --cached` cleanup to swain-doctor — untracks runtime files that leaked into git
- Add `source: swain` fingerprint to all skill frontmatters for safe legacy cleanup
- Add `references/legacy-skills.json` — machine-readable old→new skill name mapping
- Add `references/.beads-gitignore` — canonical gitignore reference for `.beads/` directories
- Add fingerprint safety check to legacy skill cleanup — third-party skills with overlapping names are never deleted

### Fixes
- Fix swain-update to use `--all` flag for non-interactive `npx skills add`
- Fix swain-init to invoke swain-doctor in Phase 4 (catches broken `.beads/.gitignore` on both fresh and existing installs)

## [1.0.0] - 2026-03-08

### New Features
- Rename all skills with `swain-` namespace prefix (swain-config, swain-design, swain-do, swain-release, swain-push, swain-update)
- Add legacy skill cleanup on session start via swain-config
- Add skill table and conflict resolution policy to AGENTS.md
- Enforce TDD methodology in implementation plans
- Add product-type branching for vision artifacts
- Implement governance skill with first-use setup
- Add release automation skill
- Add execution tracking skill (bd/beads integration)
- Add spec management skill (artifact lifecycle)
- Add swain-push skill (commit, push, conflict resolution)
- Add swain-update skill (self-updater via npx)

### Documentation
- README with full skill description table
- AGENTS.md as canonical consumer governance template
