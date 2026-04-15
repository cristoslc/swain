---
title: "Chores As A Lightweight Artifact Type"
artifact: ADR-045
track: standing
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
linked-artifacts:
  - ADR-027
  - ADR-003
depends-on-artifacts: []
evidence-pool: ""
---

# Chores As A Lightweight Artifact Type

## Context

Swain tracks work through SPECs, which follow the implementable lifecycle (Proposed → Ready → Active → Complete) with frontmatter, acceptance criteria, verification tables, and swain-do tracking. This works well for feature work, bugs, and enhancements — things that warrant planning and verification.

But not all work is a SPEC. Structural cleanup (foldering flat files, updating cross-references, renaming paths after a migration) is real work that needs tracking, but the SPEC ceremony is overhead. A chore like "folder six flat ADRs into their own directories" doesn't need acceptance criteria, a lifecycle table, or swain-do tracking — it needs a checklist and a commit.

Currently, two approaches exist: stuff it into a SPEC (overhead) or skip tracking entirely (invisible work). Neither is good.

## Decision

**Add `CHORE-NNN` as an artifact type on the `implementable` track with a reduced template.**

### Directory structure

```
docs/chores/Active/(CHORE-NNN)-<Title>/(CHORE-NNN)-<Title>.md
docs/chores/Complete/(CHORE-NNN)-<Title>/(CHORE-NNN)-<Title>.md
```

Subdirectories and foldering follow ADR-027 — same convention as every other artifact type.

### Lifecycle

```
Proposed → Active → Complete
```

Plus the universal terminal states `Abandoned` and `Superseded`. No `Ready`, `InProgress`, or `NeedsManualTest` phases. A chore is either planned or done.

### Track

`implementable` — same track as SPECs. A chore resolves when its status is `Complete`, `Abandoned`, `Retired`, or `Superseded`.

### Template

Reduced frontmatter:

```yaml
---
title: "<title>"
artifact: CHORE-NNN
track: implementable
status: Proposed | Active | Complete | Abandoned
author: <author>
created: <date>
last-updated: <date>
linked-artifacts: []
---
```

No `parent-epic`, `parent-initiative`, `swain-do`, `type`, `priority-weight`, `addresses`, `depends-on-artifacts`, or `evidence-pool`. Chores don't need that structure.

### Body sections

```
# <Title>

## Problem
One paragraph explaining what's wrong and why it matters.

## Checklist
- [ ] Item 1
- [ ] Item 2

## Notes
Optional. Anything worth capturing during the work.
```

### ID allocation

`CHORE-NNN` uses the same `next-artifact-id.sh` mechanism, with the `CHORE` prefix. Sequential numbering, same as SPECs and ADRs.

### Relationship to SPECs

Chores are not specs. They don't get implementation plans, verification tables, or swain-do tracking. If a chore grows scope beyond a simple checklist, promote it to a SPEC.

A SPEC may reference a CHORE in its `linked-artifacts` when the chore is cleanup needed before or after the spec's implementation.

## Alternatives Considered

**A. Use SPEC type:bug for chores.** Overhead. A chore like "relink cross-references after a folder rename" doesn't need acceptance criteria, verification tables, or swain-do tracking. Forcing it into SPEC format adds ceremony without value.

**B. Use tk tickets for chores.** Tickets are ephemeral execution scaffolding (ADR-015, superseded by ADR-024). They're for task tracking during implementation, not for documenting structural work that affects the artifact tree. A ticket can't express "folder these six ADRs and run relink.sh" in a way that's retrievable later.

**C. Don't track chores at all.** Invisible work. The operator asks "what about those flat ADRs?" and there's no record of the decision to fix them or whether it was done.

**D. A standalone markdown file outside docs/.** No tracking, no lifecycle, no ID allocation. It exists in a liminal space between "noticed" and "committed." The whole point of artifact types is to make work visible and trackable.

## Consequences

- **Chores are first-class artifacts.** They appear in `chart.sh` output, index files, and specgraph as implementable work items. Lightweight, but not invisible.
- **No ceremony tax.** No acceptance criteria, no verification table, no swain-do handoff. Write a checklist, do the work, mark it Complete.
- **Chore IDs are globally unique.** `CHORE-001` won't collide with `SPEC-001` or `ADR-001`. The prefix distinguishes the type.
- **Lifecycle tracks table grows by one type.** The `implementable` track now covers both SPECs and CHOREs. No new track needed — chores resolve the same way specs do.
- **`next-artifact-id.sh` needs the CHORE prefix.** The script already handles arbitrary prefixes. Add `CHORE` to its known prefixes.
- **SPEC-310 (the artifact that prompted this ADR) should be migrated to CHORE-001.** It's a checklist of cleanup tasks, not a behavior contract.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | 538e563e | Initial creation |