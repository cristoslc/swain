---
title: "Legacy pre-swain skills not cleaned up by swain-doctor"
artifact: BUG-001
status: Fixed
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
severity: low
affected-artifacts:
  - swain-doctor
discovered-in: "Manual observation — pre-swain skill directories linger in .claude/skills/ after swain adoption"
fix-ref: ""
depends-on: []
swain-do: required
---

# Legacy pre-swain skills not cleaned up by swain-doctor

## Description

swain-doctor's legacy cleanup only handles **renamed** swain skills (via the `renamed` map in `legacy-skills.json`). It has no mechanism to detect and remove **retired pre-swain skills** that have no direct replacement — they were absorbed into swain's skill set rather than renamed 1:1.

Known pre-swain skills that should be cleaned up:

- `update-agents-core` — superseded by `swain-update`
- `skill-manager` — superseded by `swain-update` / `swain-init`
- `remote-skill-manager` — superseded by `swain-update`

These may still exist in `.claude/skills/` on projects that adopted swain after previously using the standalone skill management tools.

## Reproduction Steps

1. Have a project that previously used `update-agents-core` or `skill-manager` before adopting swain
2. Run `/swain-doctor`
3. Observe that these old skill directories are not detected or removed

## Expected Behavior

swain-doctor should detect these retired pre-swain skills and remove them (with the same fingerprint safety check it uses for renamed skills).

## Actual Behavior

swain-doctor only processes the `renamed` map in `legacy-skills.json`. Skills that were retired without a 1:1 rename are invisible to the cleanup logic.

## Impact

Low severity — the stale directories don't cause errors, but they clutter `.claude/skills/` and may confuse the agent if their SKILL.md descriptions overlap with swain skills.

## Fix Approach

Add a `retired` map to `legacy-skills.json` alongside the existing `renamed` map. Each entry maps an old skill name to the swain skill that absorbed its functionality (for logging/messaging purposes only — the old directory is simply deleted, not replaced).

```json
{
  "retired": {
    "update-agents-core": "swain-update",
    "skill-manager": "swain-update",
    "remote-skill-manager": "swain-update"
  }
}
```

Update swain-doctor's legacy cleanup to process `retired` entries: same fingerprint check, but no requirement that the "replacement" exists at the old path — just verify the swain ecosystem is installed (any swain-* skill present).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Reported | 2026-03-11 | _pending_ | Initial report |
| Fixed | 2026-03-11 | _pending_ | Added retired map to legacy-skills.json, updated doctor cleanup logic |
