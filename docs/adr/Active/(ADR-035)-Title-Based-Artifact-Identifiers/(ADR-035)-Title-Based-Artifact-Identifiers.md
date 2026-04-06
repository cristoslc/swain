---
title: "Title-Based Artifact Identifiers"
artifact: ADR-035
track: standing
status: Active
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
linked-artifacts:
  - ADR-027
  - ADR-025
  - EPIC-043
  - DESIGN-006
  - DESIGN-013
depends-on-artifacts: []
evidence-pool: ""
---

# Title-Based Artifact Identifiers

## Context

Swain artifacts use serial identifiers (`SPEC-204`, `EPIC-060`) in paths, frontmatter, cross-references, and conversation. This creates two problems that reinforce each other.

**Collision prevention is costly.** Assigning the next serial requires scanning all worktrees and branches. Four completed specs target collision prevention (SPEC-156, SPEC-158, SPEC-193, SPEC-204), yet edge cases remain — untracked files, remote-only branches, and timing gaps between worktrees. The repo has 486 collision-driven renames in git history.

**Serial IDs are opaque.** `SPEC-204` says nothing about what the artifact covers. Operators and agents must look up every ID they encounter. This forces context switches in every conversation, cross-reference, and planning session. It is the more damaging of the two problems.

Titles, by contrast, almost never change. Of 607 renames in the repo, only 13 changed a title — and most of those were cosmetic (case fixes). Titles are stable enough to serve as path anchors and identifiers.

## Decision

Replace serial identifiers with title-based identifiers that include a timestamp suffix for uniqueness and ordering.

### Identifier format

```
TYPE-title-slug-DDDDhMM
```

- **TYPE** — artifact type in caps (`SPEC`, `EPIC`, `ADR`, `SPIKE`, etc.). Info scent only; uniqueness does not depend on it.
- **title-slug** — kebab-case title. The part humans say in conversation and agents match on.
- **DDDDhMM** — 7-character timestamp suffix:
  - `DDDD` — days since project epoch (2026-01-01), zero-padded decimal. 4 digits covers 27 years.
  - `h` — hour in base36 (`0`–`9` for hours 0–9, `a`–`n` for hours 10–23).
  - `MM` — minute in decimal, zero-padded.

Example: `SPEC-worktree-timestamp-bug-0086l23` — a spec created on day 86 at 21:23.

### Project epoch

The epoch is stored in project settings (e.g., `.swain/settings.json`). It can be set in several ways — during `swain-init`, on first artifact creation under this scheme, from the repo creation date, from the earliest file or artifact creation time, or manually. The method does not matter as long as the value is recorded before the first title-based identifier is assigned. Once set, the epoch must not change.

### Canonical paths and lifecycle symlinks

Each artifact lives at one canonical path. This path does not change when the artifact moves through lifecycle phases:

```
docs/spec/SPEC-worktree-timestamp-bug-0086l23/
    SPEC-worktree-timestamp-bug-0086l23.md
```

Lifecycle phase directories hold symlinks, not the artifact itself:

```
docs/spec/Active/SPEC-worktree-timestamp-bug-0086l23
    → ../SPEC-worktree-timestamp-bug-0086l23
```

A phase transition moves the symlink between lifecycle directories. The file stays put. This removes `git mv` from phase transitions and the relink cascade that follows.

### Title renames

When a title changes, rename the directory and leave a redirect symlink at the old path:

```
docs/spec/SPEC-aquatic-craft-support-0086l23/       (new canonical)
docs/spec/SPEC-worktree-timestamp-bug-0086l23       (symlink to new)
    → SPEC-aquatic-craft-support-0086l23
```

Old cross-references keep working through the redirect. New references use the new name. Redirect symlinks can be cleaned up once all references are updated.

### Collision handling

A collision needs two artifacts with the same title slug created in the same minute. For a solo project this will not happen in practice. If it does, append a digit: `SPEC-worktree-timestamp-bug-0086l232`.

### Cross-references

In frontmatter:
```yaml
artifact: SPEC-worktree-timestamp-bug-0086l23
linked-artifacts:
  - EPIC-pre-runtime-crash-recovery-0086l48
```

In prose, hyperlinked on first mention:
```markdown
This addresses the issue found in
[SPEC-worktree-timestamp-bug-0086l23](../SPEC-worktree-timestamp-bug-0086l23/).
```

In conversation: "the worktree timestamp bug spec" — the suffix disappears naturally in speech.

## Alternatives Considered

### A. UUID with late-assigned serial number

Assign a UUID at creation, then assign a `TYPE-NNN` serial on trunk post-merge. Rejected:
- Two identifiers per artifact creates confusion about which to use where.
- Late serial assignment means worktree cross-references use UUID and must be rewritten on merge.
- Serial assignment still needs collision-prevention scanning.

### B. Human-friendly UUID (word triplets)

Replace serials with generated word combos like `SPEC-bold-warm-anvil`. Three words from 1K lists give ~2B combinations. Rejected:
- The words are speakable but not meaningful. `bold-warm-anvil` tells you nothing about the artifact's purpose — the same problem as `SPEC-204` in a prettier costume.
- Operators care about what an artifact is *about*, not its label.

### C. Keep serial IDs, add UUID as metadata

Keep `TYPE-NNN` as the primary identifier but add a `uuid` frontmatter field for stable identity. Rejected:
- Serial assignment still needs worktree scanning.
- `SPEC-204` is still the opaque primary reference everywhere.
- Adds a second identifier without removing the first.

### D. Serial IDs with no changes

Keep the current system. Rejected — the collision cost is high (4 specs, 486 renames) and opaque IDs degrade every conversation.

## Consequences

**Positive:**
- Identifiers are self-describing. You know what an artifact covers from its name alone.
- No collision scanning. The timestamp suffix is computed locally with no coordination.
- Paths never change for lifecycle transitions. Symlinks replace `git mv` and remove relink cascades.
- The suffix is sortable and encodes creation order.
- Title renames work through redirect symlinks.

**Negative:**
- Identifiers are longer than `SPEC-204`. Typing the full ID in a TUI takes more keystrokes, though in speech the suffix drops away.
- The base36 hour (`a`–`n` for 10–23) requires learning one small rule.
- Migrating ~1,300 existing artifacts is a large operation. Needs its own spec.
- All tooling (`chart`, `specwatch`, `next-artifact-id.sh`, `resolve-artifact-link.sh`, skills) must learn the new format.
- Redirect symlinks build up over time if not cleaned.

**Migration:**
Migration from ~1,300 serial-ID artifacts is a major operation. The implementation epic must define the full migration path, covering at minimum:
- Global rewrite of all in-repo references (frontmatter, prose links, scripts) to use canonical paths
- Backward-compatible symlinks from old serial-ID paths to new canonical paths as a stopgap for external references (GitHub issues, bookmarks, etc.)
- After rewriting, `swain-doctor` should detect when no in-repo references point through a compat symlink and prompt the operator to decide whether to keep or prune it — external sources may still link to the old path. The operator's pruning decision should be recorded as a project-level migration choice
- Dual-format recognition in all tooling during the transition window
- Hierarchy view updates (DESIGN-013, DESIGN-014) to use canonical paths with lifecycle symlinks
- `swain-doctor` detection of unmigrated artifacts, with an interactive migration offer
- Retirement of collision infrastructure (`next-artifact-id.sh`, `fix-collisions.sh`) after migration completes
- Skill file updates (swain-design, swain-do, swain-sync, etc.) to produce and consume the new format

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-05 | — | Initial creation |
