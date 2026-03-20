---
title: "Release Branch With Squash Merge From Trunk"
artifact: ADR-013
track: standing
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
linked-artifacts:
  - ADR-011
  - ADR-012
depends-on-artifacts:
  - ADR-012
evidence-pool: ""
---

# Release Branch With Squash Merge From Trunk

## Context

[ADR-011](../Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) replaces rebase with merge for worktree landing. This produces merge commits on the development branch — correct for concurrent agent completion, but noisy for consumers who install swain skills via `npx skills add cristoslc/swain`.

The `npx skills add` command always pulls from the repository's default branch. There is no `--branch` flag. The git clone fallback also uses the default branch. This means whatever branch is set as default on GitHub is what every user installs.

Currently `main` is both the development target (where agents land work) and the distribution channel (what users install). These have conflicting requirements:

- **Development** needs full merge history, lifecycle stamps, and traceability ([ADR-012](../Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md))
- **Distribution** needs clean, infrequent updates that don't churn the consumer's install

## Decision

**Separate the development branch from the distribution branch.**

- **`trunk`** is the development branch. Agents merge here. Merge commits, lifecycle hash stamps, full artifact history. This is where all work happens.
- **`release`** is the default branch on GitHub. Updated from trunk via squash merge at release time. Each release is a single commit on this branch. This is what `npx skills add cristoslc/swain` installs.

### Branch model

```
trunk:   A──B──M──C──D──M──E──F──M──G──H
              │              │              │
release: ────S₁─────────────S₂─────────────S₃
              v0.8.0         v0.9.0         v0.10.0
```

`M` = merge commits from agent worktree landing. `S` = squash commits on release.

### Release workflow

`swain-release` handles the mechanics:

1. Determine the version bump (from conventional commits on trunk since last release tag)
2. Generate changelog from trunk's commit history
3. Tag trunk at HEAD (e.g., `v0.10.0`) — this preserves lifecycle hash reachability per [ADR-012](../Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md)
4. Squash-merge trunk into release: `git checkout release && git merge --squash trunk && git commit`
5. Tag release at HEAD with the same version tag (or a `-release` suffix if tags must be unique)
6. Push both branches and tags

### Why squash into release

- Consumers see one commit per release — clean, predictable, easy to diff between versions
- Lifecycle hashes stay on trunk where they belong — [ADR-012](../Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md) requires reachability from the development branch, not the distribution branch
- Merge commit noise from concurrent agent landing never reaches consumers
- Release commits are self-contained — each one is a complete snapshot of the skill state

### Naming: trunk, not main

The development branch is renamed from `main` to `trunk` to:
- Distinguish it from `release` (the new default) — "main" and "default" are often conflated
- Signal that `trunk` is the active development line, not the stable distribution point
- Align with the trunk-based development model this architecture follows

### Migration

Renaming `main` → `trunk` and setting `release` as default requires a one-time migration:

1. Create the `release` branch from current `main`
2. Rename `main` to `trunk`: `git branch -m main trunk`
3. Push trunk, set release as default on GitHub
4. Update all references: AGENTS.md, swain-sync, swain-dispatch, ADR-005/011 (references to `origin/main`), CI workflows
5. Update `swain-init` to configure new repos with this branch model
6. Update `swain-update` install commands if they reference `main`

## Alternatives Considered

### A. Keep main as both development and distribution

**Pros:**
- No migration needed
- Simple single-branch model

**Cons:**
- Merge commit noise from ADR-011 reaches consumers on every install
- No way to gate releases — every push to main is immediately installable
- Conflicting requirements on one branch (traceability vs cleanliness)

### B. Use tags only, no release branch

Tag releases on main. Consumers install from main but `npx skills add` could hypothetically target a tag.

**Pros:**
- No extra branch to maintain

**Cons:**
- `npx skills add` cannot target tags — it always uses the default branch
- Consumers still see every commit between releases
- No curated distribution point

### C. Use main as release, develop on a feature branch

Keep `main` as the clean default. Develop on `develop` or similar.

**Pros:**
- `main` stays clean without renaming
- Familiar gitflow-style model

**Cons:**
- Gitflow adds complexity (develop, feature, release, hotfix branches)
- "main" as the stable branch while "develop" is where work happens is confusing when the default branch is supposed to be where development occurs
- Over-engineered for a solo-operator project with agent swarming

## Consequences

**Positive:**
- Clean distribution channel — consumers get one commit per release
- Full development history preserved on trunk — lifecycle stamps, merge commits, artifact traceability all intact
- Release gating — operator decides when to cut a release, not when an agent finishes a task
- `npx skills add` installs stable, tested releases by default

**Accepted downsides:**
- Two-branch model adds maintenance — `swain-release` must handle the squash-merge workflow
- Renaming main → trunk requires a one-time migration across all references (AGENTS.md, CI, skill files, ADRs)
- Contributors must know to target trunk, not release, for PRs
- Tags on both branches may cause confusion if not clearly documented

**Constraints imposed:**
- `swain-release` must be updated to support the squash-merge workflow
- `swain-init` must configure new repos with `trunk` + `release` branch model
- `swain-sync` and `swain-dispatch` must target `trunk`, not `main`
- All existing references to `main` in skill files and ADRs must be updated

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Drafted alongside ADR-011 and ADR-012 |
| Active | 2026-03-20 | 54e12dc | Adopted; trunk+release branch model |
