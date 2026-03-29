---
title: "Remove Tmux-Based swain-stage"
artifact: SPEC-177
track: implementable
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
priority-weight: high
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-015
linked-artifacts:
  - SPEC-125
  - SPEC-127
  - DESIGN-004
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Remove Tmux-Based swain-stage

## Problem Statement

The old tmux-based swain-stage (workspace layouts, MOTD panel, pane management) is dead weight. [INITIATIVE-015](../../../initiative/Active/(INITIATIVE-015)-swain-stage-Redesign/(INITIATIVE-015)-swain-stage-Redesign.md) has committed to a browser-based replacement, and [DESIGN-004](../../../design/Active/(DESIGN-004)-swain-stage-Interaction-Design/(DESIGN-004)-swain-stage-Interaction-Design.md) captures the new interaction design. The old code remains in `skills/swain-stage/`, hooks remain registered in settings, and two bug-fix specs ([SPEC-125](../(SPEC-125)-Stage-Hooks-Fire-Unconditionally/SPEC-125.md), [SPEC-127](../(SPEC-127)-Stage-Hook-ENOENT-Dead-CWD/SPEC-127.md)) target code that should be deleted rather than fixed.

## Desired Outcomes

Eliminates confusion between old tmux-stage and new browser-stage directions. Removes hook noise from non-stage sessions (the problem SPEC-125 was trying to fix). Unblocks the new browser-based swain-stage by clearing the namespace.

## External Behavior

**Inputs:** None (removal spec).

**Postconditions:**
- `skills/swain-stage/` directory no longer exists
- No tmux-related hooks remain in `.claude/settings.json` or `.claude/settings.local.json`
- The `swain-stage` skill description no longer references tmux
- SPEC-125 and SPEC-127 are transitioned to Abandoned with a note referencing this spec

## Acceptance Criteria

- **Given** the spec is complete, **When** `ls skills/swain-stage/` is run, **Then** the directory does not exist
- **Given** the spec is complete, **When** `.claude/settings.json` is inspected, **Then** no references to `stage-status-hook.sh`, `swain-motd`, or `swain-stage.sh` remain in hook definitions
- **Given** the spec is complete, **When** `AGENTS.md` and `AGENTS.content.md` are inspected, **Then** no references to tmux layout presets, MOTD panel, or the old swain-stage behavior remain
- **Given** the spec is complete, **When** `grep -r "swain-stage" skills/ .claude/skills/` is run, **Then** the only matches are the new browser-based skill definition (if it exists yet) or zero matches
- **Given** the spec is complete, **When** SPEC-125 and SPEC-127 are inspected, **Then** both are in `Abandoned` phase with lifecycle entries citing SPEC-177

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| `ls skills/swain-stage/` returns not found | Directory deleted via `rm -rf` | Pass |
| No stage hooks in `.claude/settings.json` | `grep` returns 0 matches for `stage-status-hook`, `swain-motd`, `swain-stage.sh` | Pass |
| No tmux-stage refs in AGENTS.md/AGENTS.content.md | `grep -ic` returns 0 for both files | Pass |
| `grep -r swain-stage skills/` returns zero matches | All references cleaned from swain-session, swain, swain-status, swain-help, swain-doctor, swain-init, README | Pass |
| SPEC-125 and SPEC-127 in Abandoned phase | Both moved to `docs/spec/Abandoned/`, status frontmatter updated, lifecycle entries cite SPEC-177 | Pass |

## Scope & Constraints

**In scope:**
- Delete `skills/swain-stage/` (SKILL.md, scripts/swain-stage.sh, scripts/swain-motd.py, scripts/swain-motd.sh, scripts/stage-status-hook.sh, references/layouts/*.json, references/yazi/*)
- Remove tmux-stage hook registrations from settings files
- Remove tmux-stage references from AGENTS.md/AGENTS.content.md
- Transition SPEC-125 and SPEC-127 to Abandoned
- Update or remove the swain-stage skill description so it no longer advertises tmux functionality

**Out of scope:**
- Building the new browser-based swain-stage (that's SPEC-093 and future work under INITIATIVE-015)
- Removing tmux as a dependency entirely (tmux may still be used for other purposes)
- Modifying the swain-session skill (it has its own tmux tab-naming logic that is independent of swain-stage)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | 57c7822 | Initial creation — removal of dead tmux-stage code |
