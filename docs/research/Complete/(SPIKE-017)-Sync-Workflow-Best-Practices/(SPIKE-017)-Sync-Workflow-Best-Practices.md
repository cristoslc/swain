---
title: "Sync Workflow Best Practices"
artifact: SPIKE-017
track: container
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Beyond fetch-first and security scanning, what workflow habits should swain-sync enforce or encourage for clean, safe git collaboration?"
gate: Pre-EPIC-012-specs
risks-addressed:
  - Missing workflow habits that other tools enforce by default
  - Over-engineering the sync workflow with rarely useful checks
linked-artifacts:
  - EPIC-012
trove: ""
---

# Sync Workflow Best Practices

## Question

Beyond fetch-first and security scanning, what workflow habits should swain-sync enforce or encourage for clean, safe git collaboration?

## Go / No-Go Criteria

- **GO:** At least 2 additional habits identified that meaningfully reduce foot-gun risk in solo or small-team workflows
- **NO-GO:** All additional habits add friction without measurable safety improvement — keep swain-sync focused on fetch-first + security scanning

## Pivot Recommendation

If no additional habits are worth enforcing, keep swain-sync lean and document the "nice-to-have" practices in a runbook instead of baking them into the tool.

## Areas to investigate

- Stash/pop dirty working tree handling
- Rebase vs merge strategy configuration
- Branch protection awareness (don't push to protected branches)
- Commit message linting / conventional commits enforcement
- Pre-push hook verification
- Conflict resolution strategies
- Large file detection (prevent accidental binary commits)
- Sign-off / GPG signing enforcement

## Findings

### Verdict: GO

Four additional habits provide measurable safety improvement in solo and small-team workflows without excessive friction.

### Recommended Habits (enforce by default)

| Habit | What it does | Why it matters | Friction |
|-------|-------------|----------------|----------|
| **Dirty stash/pop** | Stash uncommitted changes before rebase, pop after | Prevents "your local changes would be overwritten" failures and lost work | Zero — transparent to user |
| **Branch protection check** | Warn (don't block) if pushing directly to main/master/production | Prevents accidental commits to protected branches, especially in teams | Low — one-time warning, overridable |
| **Large file detection** | Warn on files >1MB, block on files >10MB staged for commit | Prevents repo bloat from accidental binary/media commits. Git repos degrade with large files (every clone pays forever) | Low — only fires on large files |
| **Divergence detection** | After fetch, check if local branch has diverged (force-push scenario) and warn | Prevents silent history overwrites. If local and remote have diverged beyond rebase, user needs to choose a strategy | Low — only fires on divergence |

### Evaluated but excluded

| Habit | Why excluded |
|-------|-------------|
| **Rebase vs merge strategy config** | Already handled by swain-push's `pull --rebase` default. Adding configurability adds complexity without clear benefit for the target audience (solo/small-team). |
| **Commit message linting** | Already enforced by swain-push's conventional commit generation. Linting agent-generated messages is circular. |
| **Pre-push hook verification** | Git's built-in pre-push hooks already run. Adding swain-level verification duplicates git's mechanism. |
| **GPG/SSH signing enforcement** | Already handled by swain-keys. Adding signing checks to sync creates tight coupling between skills. |
| **Conflict resolution strategies** | Current behavior (abort rebase, show conflicting files, ask user) is correct. Auto-resolution strategies are too risky for a general-purpose tool. |

### Implementation Priorities

1. **Dirty stash/pop** — highest ROI, zero friction, prevents the most common failure mode
2. **Large file detection** — second highest ROI, prevents permanent repo damage
3. **Branch protection check** — useful for team workflows, no cost to solo developers
4. **Divergence detection** — edge case but catastrophic when it hits

### Configuration Surface

All habits should be configurable via `swain.settings.json`:

```json
{
  "sync": {
    "stashBeforeRebase": true,
    "warnProtectedBranches": ["main", "master", "production"],
    "maxFileSizeWarnMB": 1,
    "maxFileSizeBlockMB": 10,
    "warnOnDivergence": true
  }
}
```

Defaults are shown above — all habits enabled, conservative thresholds.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 34f2d62 | Initial creation |
| Complete | 2026-03-13 | ef4d358 | GO: 4 sync habits recommended |
