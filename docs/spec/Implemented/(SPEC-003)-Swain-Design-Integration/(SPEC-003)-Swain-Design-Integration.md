---
title: "swain-design Integration"
artifact: SPEC-003
status: Implemented
author: cristos
created: 2026-03-09
last-updated: 2026-03-11
parent-epic: EPIC-001
addresses: []
swain-do: required
linked-artifacts: []
depends-on-artifacts:
  - SPEC-001
---

# swain-design Integration

## Problem Statement

swain-design needs to know about evidence pools so it can offer them during research phases (spike Active, ADR research) and so artifacts can link to pools with commit-hash pinning.

## External Behavior

### Artifact frontmatter addition

All artifact templates gain an optional `evidence-pool` field:

```yaml
evidence-pool: <pool-id>@<commit-hash>
```

### Research phase hook

When swain-design transitions a spike to Active or begins ADR research:

1. Check `docs/evidence-pools/*/manifest.yaml` for pools with matching tags
2. If matches found: "Found N existing evidence pool(s) that may be relevant: [list]. Use one, or create a new pool?"
3. If no matches: "No existing evidence pools match. Want to create one with swain-search?"
4. If the user wants a pool, invoke swain-search

### Back-link maintenance

When an artifact adds `evidence-pool: <pool-id>@<hash>` to its frontmatter, the pool's `manifest.yaml` should get a corresponding `referenced-by` entry. swain-design handles this during artifact creation/update.

## Acceptance Criteria

1. **Given** a spike transitioning to Active, **when** matching evidence pools exist, **then** swain-design lists them and offers to link or create new.
2. **Given** an artifact with `evidence-pool` in frontmatter, **when** the artifact is created/updated, **then** the pool's manifest gets an updated `referenced-by` entry.
3. **Given** the spike/ADR template, **when** rendered, **then** it includes the optional `evidence-pool` field.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-09 | — | Initial creation |
| Approved | 2026-03-11 | — | Approved for implementation |
| Implemented | 2026-03-13 | 5fd2e44 | Transitioned — evidence-pool field, research hook, back-links |
