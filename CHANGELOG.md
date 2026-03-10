# Changelog

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
