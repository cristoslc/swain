# Changelog

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
