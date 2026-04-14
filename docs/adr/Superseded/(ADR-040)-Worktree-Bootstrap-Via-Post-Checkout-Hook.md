---
title: "Worktree bootstrap via tracked post-checkout hook"
artifact: ADR-040
track: standing
status: Superseded
superseded-by: ADR-042
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
linked-artifacts:
  - SPEC-305
  - SPEC-290
  - ADR-041
  - ADR-042
depends-on-artifacts: []
evidence-pool: ""
---

# Worktree bootstrap via tracked post-checkout hook

## Context

Git worktrees do not inherit the contents of gitignored directories from the common root. Swain relies on several such directories: skill trees, bin symlinks, runtime state, and peer-agent dot-folders. A worktree without these symlinks looks uninitialized. Skills fail to resolve. Onboarding re-runs. Sessions lose shared state.

Swain bootstraps these symlinks today, but in scattered places. `create_session_worktree` in `bin/swain` handles worktrees that swain creates. The `using-git-worktrees` skill calls raw `git worktree add` and skips the step. Pre-existing worktrees never got the symlinks at all. [SPEC-290](../../spec/Active/(SPEC-290)-swain-init-not-symlinked-into-pre-existing-worktrees) patched one case — the `.swain-init` marker — by teaching swain-doctor to repair it. Every new worktree-adjacent skill would inherit the same problem and need the same ritual.

The fix must be structural. It must run automatically on every worktree creation, from any tool. It must not depend on a particular entry point.

## Decision

Install a tracked `post-checkout` hook in the repo. Point `core.hooksPath` at the tracked directory. Git runs the hook after every `git worktree add` and every checkout inside a worktree. The hook reads the shared dir list, walks each entry in the common root, and creates any missing symlinks into the current worktree.

All worktree-adjacent swain code must defer bootstrap to this hook. No skill, script, or shim creates worktree symlinks on its own. `create_session_worktree` stops symlinking inline. `using-git-worktrees` stops symlinking. swain-doctor keeps a repair pass, but only as a safety net for worktrees that pre-date the hook and for stale or broken links.

## Alternatives Considered

- **Keep ad-hoc symlinking in each entry point.** The current state. Leaves drift across `bin/swain`, `using-git-worktrees`, and swain-doctor. Breaks for any new worktree creator.
- **Shim `git` via a wrapper.** Would catch every `worktree add` call. Brittle. Breaks IDE integrations and tooling that invokes the real `git` binary.
- **Move shared dirs into the common git dir.** Structural. But forces every script to path-resolve via `$GIT_DIR` instead of `$REPO_ROOT`. Breaks conventions used across the repo and in skills.
- **Global git template via `init.templateDir`.** Runs on `git init` and `git clone`. Does not run on `git worktree add`. Not a fit.

## Consequences

- **Single bootstrap surface.** The hook is the only place that creates worktree symlinks. All skills defer to it.
- **`core.hooksPath` is a managed config.** swain-init sets it during onboarding. If a consumer already uses `core.hooksPath`, swain must chain rather than overwrite.
- **Hook script lives in the tracked tree.** It gets versioned with the repo and survives clones. A reasonable location is `.swain/hooks/` once [ADR-041](ADR-041-Swain-Runtime-State-Location) lands.
- **swain-doctor becomes a safety net.** Its role shrinks to repairing pre-hook worktrees and stale symlinks. The primary mechanism is the hook.
- **Hook must be fast and idempotent.** It runs on every checkout, not just worktree add. Leaving existing symlinks alone is required.
- **Windows and symlink-hostile platforms need a fallback.** Not scoped here. Defer to the portability track.
- **Consumer `.git/config` gets a `core.hooksPath` entry.** Shown in the swain-init preview and confirmed before write.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |
| Superseded | 2026-04-13 | — | Superseded by ADR-042. Tracking all runtime and peer-agent dirs removes the need for a post-checkout hook. |
