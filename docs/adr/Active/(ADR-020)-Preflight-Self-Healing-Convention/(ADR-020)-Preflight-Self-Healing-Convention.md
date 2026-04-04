---
title: "Preflight Self-Healing Convention"
artifact: ADR-020
track: standing
status: Active
author: cristos
created: 2026-03-29
last-updated: 2026-03-29
linked-artifacts:
  - ADR-019
  - ADR-029
  - EPIC-047
  - SPEC-186
  - SPEC-191
  - SPEC-255
depends-on-artifacts: []
evidence-pool: ""
---

# Preflight Self-Healing Convention

## Context

The swain preflight (`swain-preflight.sh`) runs at session start and gates whether swain-doctor is invoked. It was originally designed to **detect** issues and **report** them so the doctor could remediate. In practice, many checks can repair their own findings without operator input — and when they don't, the operator gets an error message instead of a working session.

This became visible during the ADR-019 implementation (EPIC-047). The preflight checked for `.agents/bin/swain-trunk.sh` and reported it missing, but had all the information needed to create the symlink itself. The fix was trivial: add `mkdir -p` and `ln -sf` to the check. Once the self-healing pattern was applied to `.agents/bin/` symlinks (SPEC-186) and `bin/` symlinks (SPEC-188), those checks went from "report and escalate" to "repair and continue" — the operator never sees the issue.

## Decision

Preflight checks **must self-heal when repair is safe and deterministic.** A check should only report-without-repairing when one of these conditions holds:

### When to report only (not repair)

1. **Repair requires operator judgment.** The check can't determine the correct fix without context the operator has. Example: a real file (not a symlink) exists at a path where a symlink is expected — overwriting could destroy the operator's work.

2. **Repair is destructive.** The fix involves deleting or modifying content the operator may want to preserve. Example: stale worktrees with uncommitted changes.

3. **Repair has side effects beyond the local project.** The fix would modify global state (dotfiles, system config, git global config). Example: commit signing configuration.

### When to self-heal (silent)

Everything else that is local to the project. If the check has enough information to fix the issue, and the fix is:
- **Idempotent** — running twice produces the same result
- **Non-destructive** — creates or updates without deleting operator content
- **Local** — affects only the project directory
- **Deterministic** — the correct fix is unambiguous from the project state

Then the check should fix it silently (or with an advisory log line) and continue.

### When to bundle and offer (operator consent)

Some fixes are deterministic and non-destructive but affect state beyond the project directory — installing system packages, configuring user-level tools, or writing to `~/.config`. These fixes are safe but require operator consent because they change the operator's environment.

Doctor **collects** all such findings during its scan, then **presents a single bundled fix plan** at the end. The operator reviews the plan and approves or declines as a batch. Doctor never runs external installs mid-scan or one at a time.

Bundle-and-offer applies when the fix is:
- **Deterministic** — the correct action is unambiguous
- **Non-destructive** — installs or creates, never deletes
- **Beyond project scope** — touches system packages, user config, or global state
- **Reversible** — the operator can undo it (e.g., `brew uninstall`)

Examples: missing optional tools (`brew install rtk`, `brew install gh`), user-level config that a tool needs.

The bundled plan format:

```
Doctor found 3 fixable issues:

  1. rtk not installed — git-compact passes through without compression
     Fix: brew install rtk

  2. tmux not installed — session tab-naming unavailable
     Fix: brew install tmux

  3. gh not installed — GitHub issues integration unavailable
     Fix: brew install gh

Run all fixes? [y/N]
```

If the operator declines, doctor logs the findings as advisories and continues. No blocking.

### Advisory logging

Self-healing checks emit an advisory line so the operator knows what happened:
```
advisory: repaired 3 .agents/bin/ symlink(s) (ADR-019)
```

Advisory lines are informational — they don't count as issues and don't trigger swain-doctor invocation.

### Classification template

When adding a new preflight check, classify it:

| Check | Action | Reason |
|-------|--------|--------|
| `.agents/bin/` symlink missing | Self-heal | Create from skill tree — local, idempotent |
| Flat-file artifact needs foldering | Self-heal | `doctor --fix-flat-artifacts` — local, deterministic |
| Optional tool missing (`rtk`, `gh`, `tmux`) | Bundle and offer | `brew install` — non-destructive but beyond project scope |
| Governance block stale | Report only | Operator may have intentional differences |
| Real file conflicts with symlink | Report only | Could destroy operator work |
| Commit signing not configured | Report only | Modifies global git config |

## Alternatives Considered

**Report-only preflight, doctor repairs.** The original design. Creates a two-step process (detect in preflight, repair in doctor) for issues that could be fixed in one step. The doctor invocation costs tokens and time for repairs that take milliseconds.

**Silent self-healing with no logging.** Simpler but opaque. The operator would never know the preflight fixed something, making debugging harder when the repair itself is wrong.

**Always escalate to doctor.** Ensures operator visibility but means every session with a repairable issue invokes the full doctor flow, which is heavyweight for a missing symlink.

**Offer each fix individually.** Doctor prompts for each finding one at a time. Creates prompt fatigue when multiple tools are missing. The bundled approach respects operator attention by collecting all findings first.

## Consequences

**Positive:**
- Most sessions start clean without doctor invocation, even after skill updates or worktree creation.
- Operators see fewer error messages for issues they can't meaningfully act on.
- New checks have a clear decision framework: can I fix it? → fix it.

**Accepted downsides:**
- The preflight becomes more than a read-only check — it modifies the filesystem. This is intentional but changes its conceptual role from "observer" to "maintainer."
- Self-healing masks issues that might indicate deeper problems. Mitigated by advisory logging — the operator can review if curious.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-29 | — | Surfaced during RETRO-2026-03-29-adr-019-script-convention |
| Active | 2026-04-03 | -- | Extended with bundle-and-offer pattern for external installs |
