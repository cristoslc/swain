---
title: "Python Tooling Support for CHORE Type"
artifact: SPEC-312
track: implementable
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
type: enhancement
parent-epic: EPIC-077
linked-artifacts:
  - [SPEC-311](../(SPEC-311)-Bash-Script-Support-for-CHORE-Prefix/(SPEC-311)-Bash-Script-Support-for-CHORE-Prefix.md)
  - [ADR-045](../../../adr/Active/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type.md)
depends-on-artifacts:
  - SPEC-311
addresses:
  - PERSONA-002
swain-do: required
---

# Python Tooling Support for CHORE Type

## Problem Statement

The `specgraph` Python package and `specwatch.sh` (Python section) don't know about the CHORE type. `xref.py` will skip CHORE references, `materialize.py` will build incorrect paths (`docs/chore/` instead of `docs/chores/`), and `specwatch.sh` won't detect CHOREs in wrong phase directories.

## Scope

### 1. `specgraph/xref.py`

- Add `"CHORE"` to `_KNOWN_ARTIFACT_PREFIXES` (lines 10-13). Without this, `CHORE-001` in markdown link text won't be detected as a cross-reference.

### 2. `specgraph/materialize.py`

- Add an explicit mapping for `"CHORE" → "chores"` in the type-to-directory logic (around line 166-167). The current code lowercases the type to build paths, which would produce `docs/chore/` instead of `docs/chores/`.

### 3. `specgraph/resolved.py`

- Optionally add `"CHORE"` to `_IMPLEMENTABLE_TYPES` (or add a comment noting CHORE falls through to the implementable track by default). This is a clarity improvement, not a functional requirement — the current fallback already handles it correctly.

### 4. `specwatch.sh` (embedded Python)

- Add `'chores'` to the `TYPE_DIRS` set (around line 936). Without this, specwatch won't detect CHORE files in mis-placed phase directories.

### 5. `rebuild-index.sh`

- Add `chores` case to the type-to-directory and type-to-title mappings (lines 4, 16-18, 32-45). This enables `rebuild-index.sh chores` to generate `docs/chores/list-chores.md`.

## Acceptance Criteria

- [ ] `chart xref` detects CHORE-NNN references in markdown body text
- [ ] `chart build` includes CHORE artifacts in the graph with correct directory paths
- [ ] `chart scope CHORE-001` returns a valid scope chain
- [ ] `rebuild-index.sh chores` generates `docs/chores/list-chores.md`
- [ ] `specwatch.sh scan` processes CHORE files and detects phase mismatches

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| `chart xref` | CHORE-001 references detected | |
| `chart build` | CHORE-001 appears in graph at correct path | |
| `chart scope` | Returns scope chain for CHORE-001 | |
| `rebuild-index.sh` | Generates `list-chores.md` with CHORE-001 entry | |
| `specwatch scan` | Detects CHORE artifacts | |

## Scope & Constraints

- **In scope:** Python modules listed above, `specwatch.sh`, `rebuild-index.sh`
- **Out of scope:** Bash scripts (SPEC-311), skill docs (SPEC-313)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
4ce9b173 Initial creation |