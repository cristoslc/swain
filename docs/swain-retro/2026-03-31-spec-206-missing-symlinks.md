---
title: "Retro: SPEC-206 missing session greeting symlinks"
artifact: RETRO-2026-03-31-spec-206-missing-symlinks
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "SPEC-206 bug fix and test gap remediation for .agents/bin/ symlinks"
period: "2026-03-31"
linked-artifacts:
  - SPEC-206
  - SPEC-186
  - ADR-019
---

# Retro: SPEC-206 missing session greeting symlinks

## Summary

SPEC-206 was filed as a bug for a missing script (`swain-session-greeting.sh`). Investigation revealed the script already existed from SPEC-194 — only its `.agents/bin/` symlink was missing. The fix expanded to cover four gaps: the missing symlinks themselves, doctor symlink validation, test path coverage, and scan scope (`.py` files were excluded).

## Reflection

### What went well

- ADR-019 and SPEC-186 already established the right pattern for symlink management (`os.path.relpath` for portable paths, preflight auto-repair). Aligning the doctor check with existing convention avoided inventing a parallel approach.
- The existing test infrastructure (`test-session-greeting.sh`, `test-swain-doctor-sh.sh`) was straightforward to extend. Both test suites expanded without structural changes.

### What was surprising

- The bug was a missing symlink, not a missing script. SPEC-194 shipped the implementation but never committed the symlink. The spec was over-scoped for the actual defect.
- Preflight auto-repair (SPEC-186) runs at session start and would have fixed this at runtime — but in the swain source repo where `.agents/bin/` is tracked in git, runtime repairs are ephemeral and don't persist. The preflight safety net has a blind spot in repos that version-control `.agents/bin/`.
- Four other scripts were also missing symlinks (`swain-preflight-timing.sh`, `swain-worktree-overlap.sh`, `swain-startup-timing.sh`) and one was broken (`specgraph.py` — target renamed to `specgraph_entry.py`). These were silent failures.

### What would change

- **Worktree discipline was violated.** Mutating work started on trunk. The operator had to redirect twice ("shouldn't you have worktreed?" and "you keep trying to do that interactively, use force"). This is a recurring pattern — agents default to the path of least resistance rather than following isolation protocol.
- **Pre-plan detection was skipped.** `git log` would have shown SPEC-194's implementation commits immediately, avoiding an over-scoped bug spec. The swain-do pre-plan detection step exists precisely for this — it should be habitual even for "obvious" bugs.

### Patterns observed

- **Symlink-as-deployment-artifact**: `.agents/bin/` symlinks are the deployment mechanism for agent-facing scripts. A script without its symlink is like a binary without a PATH entry — it exists but is unreachable. The doctor check now catches this, but the root cause is that symlink creation isn't part of the script creation workflow.
- **Test path vs deployment path divergence**: Tests that exercise source files directly (`$SCRIPT_DIR/script.sh`) pass even when the deployed interface (`.agents/bin/script.sh`) is broken. This is analogous to testing a function by importing from source rather than through the public API.

## SPEC candidates

1. **Symlink auto-creation on script commit** — when a new executable is added to `skills/*/scripts/`, a pre-commit hook or swain-init refresh step should create the `.agents/bin/` symlink automatically. Currently this requires manual action or waiting for preflight repair.
2. **Preflight persistence in source repos** — preflight auto-repairs `.agents/bin/` symlinks at runtime but doesn't stage or commit the changes. In repos that track `.agents/bin/` (like swain itself), repairs are lost on the next clean checkout. Preflight should detect tracked `.agents/bin/` and offer to commit repairs.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Worktree discipline violation | feedback memory | Agent started mutating trunk without isolation — operator redirected twice |
| Symlink auto-creation on script commit | SPEC candidate | New scripts in skills/*/scripts/ need automatic symlink creation |
| Preflight persistence in source repos | SPEC candidate | Auto-repairs should commit when .agents/bin/ is tracked |
