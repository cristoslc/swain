# Chores (CHORE-NNN)

**Template:** [chore-template.md.template](chore-template.md.template)

**Lifecycle track: Implementable**

```
mermaid
stateDiagram-v2
    [*] --> Active
    Active --> Complete
    Complete --> [*]
    Active --> Abandoned
    Abandoned --> [*]
```

A Chore is lightweight cleanup work — small, bounded, and independently executable. It does not ship feature code. Chores are the appropriate type for file moves, renames, relinking, index generation, and other infrastructure hygiene tasks.

## Reduced frontmatter

Chores omit fields that are not relevant to lightweight cleanup work:

- **No `parent-epic`** — chores are standalone; they don't need epic coordination
- **No `swain-do`** — chores are typically one task; plan creation is optional
- **No `type`** — chores don't have feature/bug variants
- **No `priority-weight`** — chores are uniformly low-priority cleanup
- **No `addresses`** — chores don't address personas

## Folder structure

`docs/chores/<Phase>/(CHORE-NNN)-<Title>/` — the chore folder lives inside a subdirectory matching its current lifecycle phase. Phase subdirectories: `Proposed/`, `Active/`, `Complete/`.

- Example: `docs/chores/Active/(CHORE-001)-Artifact-Cleanup/`
- Primary file: `(CHORE-NNN)-<Title>.md` — the chore document itself.
- When transitioning phases, **move the folder** to the new phase directory.

## Body sections

- **Problem** — what needs to be cleaned up and why
- **Checklist** — concrete steps to complete the chore
- **Notes** — any relevant context or follow-up items

## Relationship to ADR-045

This artifact type was established by ADR-045. Chores track alongside SPECs in the implementable track but use a simplified lifecycle (Active → Complete, no Proposed/Ready/InProgress phases).