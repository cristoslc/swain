---
title: "Track runtime and peer-agent dirs instead of symlinking via hook"
artifact: ADR-042
track: standing
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
linked-artifacts:
  - ADR-040
  - ADR-041
  - SPEC-305
  - EPIC-076
depends-on-artifacts: []
evidence-pool: ""
---

# Track runtime and peer-agent dirs instead of symlinking via hook

## Context

[ADR-040](../Superseded/(ADR-040)-Worktree-Bootstrap-Via-Post-Checkout-Hook.md) proposed a tracked `post-checkout` hook to symlink gitignored directories into worktrees. At the time, the plan was to gitignore the entire `.swain/` directory plus peer-agent dot-folders (`.claude/`, `.cursor/`, etc.). Worktrees do not inherit gitignored content, so a hook was needed.

[ADR-041]((ADR-041)-Swain-Runtime-State-Location.md) narrowed the gitignore. Only `.swain/session/` is ignored. Everything else under `.swain/` is tracked. That change removes most of the hook's reason to exist. Tracked files appear in worktrees automatically via git.

The remaining candidates for symlinking were `.swain-init` (ignored) and peer-agent dirs (ignore status varies by consumer). But `.swain-init` should just be tracked. And peer-agent dirs should also be tracked when `.agents/` is tracked, since the `.agents/` spec treats those directories as canonical agent config that teams may want to share. If a consumer chooses to ignore a peer-agent dir, that is their decision — swain does not compensate for consumer gitignore choices with a hook.

## Decision

**Track everything that swain or peer agents need in worktrees.** No gitignored directories need symlinking. Therefore, no post-checkout hook is needed for worktree bootstrap.

1. **`.swain-init` is tracked.** Move it out of the gitignore block. It is a project-level marker that says "swain has been set up here." Worktrees should see it.
2. **Peer-agent dirs are tracked by default.** When `.agents/` is tracked, dirs like `.claude/`, `.cursor/`, and `.aider/` should also be tracked. They contain agent rules, skills, and config that benefit from version control. The operator can gitignore any of them, but swain will not install a hook to compensate.
3. **No post-checkout hook.** ADR-040's hook is unnecessary. The only ignored path under `.swain/` is `.swain/session/`, which should not be symlinked — worktrees get their own session or none.
4. **Delete inline symlinking in `bin/swain`.** The `create_session_worktree()` function currently symlinks skill dirs, `.swain-init`, and peer-agent dirs. Remove those blocks. Tracked files make them redundant.
5. **Downgrade swain-doctor symlink repair.** The repair pass becomes dead code once inline symlinking is removed. Remove or stub it.

## Alternatives Considered

- **Keep the hook as a safety net.** Adds complexity and a `core.hooksPath` config change for no material benefit. Tracked files already appear in worktrees. A hook that re-creates what git already provides is pure overhead.
- **Keep the hook only for peer-agent dirs.** ADR-041 already decided swain does not impose gitignore policy for peer-agent dirs. A hook that compensates for consumer gitignore choices contradicts that decision.
- **Keep inline symlinking in `bin/swain`.** Redundant with tracked files. Creates a hidden dependency on a symlink ritual that is not needed. Makes the worktree story harder to understand.
- **Gitignore `.swain-init` but symlink it.** Adds a gitignore entry plus a symlink path for a file that should simply be tracked.

## Consequences

- **Worktree bootstrap is just `git worktree add`.** No hooks, no symlinking, no doctor repair. The simplest possible mechanism.
- **`.swain-init` appears in `git status` as a tracked file.** Operators will see it in diffs. It is a zero-byte marker — low noise.
- **Peer-agent dirs appear in `git status` if they exist.** This is already the case for `.agents/`. Tracking peer-agent dirs is consistent.
- **`core.hooksPath` is not set by swain.** One fewer config change during onboarding. No chaining concerns.
- **`using-git-worktrees` skill simplifies.** No symlinking steps needed. Creation is just `git worktree add` plus project setup.
- **swain-doctor loses its symlink repair pass.** Check 12 and the SPEC-290 repair become dead code. Remove them.
- **ADR-040 is superseded.** Its premise (gitignored dirs need a hook) no longer holds.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation; supersedes ADR-040 |