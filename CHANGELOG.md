# Changelog

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
