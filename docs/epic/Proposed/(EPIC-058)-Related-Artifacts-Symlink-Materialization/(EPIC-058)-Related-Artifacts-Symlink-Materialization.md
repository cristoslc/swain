---
title: "Related Artifacts Symlink Materialization"
artifact: EPIC-058
status: Proposed
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
parent-initiative: INITIATIVE-002
linked-artifacts:
  - DESIGN-016
artifact-refs:
  - artifact: DESIGN-016
    rel: [aligned]
depends-on-artifacts: []
success-criteria:
  - Projection includes linked_artifacts and depends_on_artifacts fields
  - _Related/ symlinks created for cross-references
  - _Depends-On/ symlinks created for dependencies
  - Stale symlinks cleaned up on rebuild
  - All tests pass
---

# Related Artifacts Symlink Materialization

## Overview
Extend the materialization system to create `_Related/` and `_Depends-On/` symlink directories, making all graph edges browseable from the filesystem.

## Scope
This epic delivers:
1. Extended projection schema with relationship fields
2. `_Related/` symlink creation for `linked-artifacts` and `artifact-refs`
3. `_Depends-On/` symlink creation for `depends-on-artifacts`
4. Cleanup logic for stale relationship symlinks

## Success Criteria
- [ ] Projection records include `linked_artifacts` field
- [ ] Projection records include `depends_on_artifacts` field
- [ ] `_Related/` directory created with correct symlinks
- [ ] `_Depends-On/` directory created with correct symlinks
- [ ] Stale symlinks removed on rebuild
- [ ] Broken references skipped gracefully
- [ ] All existing tests pass
- [ ] New tests for relationship materialization

## Child SPECs
- SPEC-248: Extend Projection Schema with Relationship Fields
- SPEC-249: Materialize Related Artifacts Symlinks
- SPEC-250: Cleanup Stale Relationship Symlinks

## Dependencies
- DESIGN-013 (Hierarchy Materialization Contract)
- DESIGN-014 (Placement and Unparented Surfaces)
- Existing materialization infrastructure

## Risks
- Performance: additional edges to process (mitigated by efficient edge queries)
- Complexity: more symlink types (mitigated by clear separation of concerns)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-03 | pending | Initial creation |