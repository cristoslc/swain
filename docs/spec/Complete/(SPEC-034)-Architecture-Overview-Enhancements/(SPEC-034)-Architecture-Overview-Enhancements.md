---
title: "Architecture Overview Enhancements"
artifact: SPEC-034
track: implementable
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
type: enhancement
parent-epic:
linked-artifacts:
  - VISION-001
  - SPEC-031
depends-on-artifacts: []
addresses: []
source-issue: github:cristoslc/swain#44
swain-do: required
---

# Architecture Overview Enhancements

## Problem Statement

Architecture overviews (`architecture-overview.md`) are currently only recognized at the Vision level, but Epics often need their own narrower architectural documentation. Additionally, there is no enforcement that architecture overviews include a diagram — text-only architecture docs lose critical information about component relationships and data flow.

## External Behavior

### 1. Epic-level architecture overviews

Architecture overviews are valid alongside both Vision and Epic artifacts:
- `docs/vision/<Phase>/(VISION-NNN)-Title/architecture-overview.md`
- `docs/epic/<Phase>/(EPIC-NNN)-Title/architecture-overview.md`

`specgraph scope <ID>` detects architecture overviews at the nearest level in the parent chain — if the artifact's parent Epic has one, show it; if not, walk up to the Vision level.

`specgraph overview` notes which active Epics/Visions have architecture overviews.

### 2. Diagram requirement

Every architecture overview must contain at least one diagram. Acceptable formats:
- Mermaid code block (` ```mermaid `)
- Image reference (standard markdown `![alt](path)` syntax pointing to a local or remote image)
- A `## Diagram` or `## Architecture Diagram` section heading (for externally-hosted diagrams)

### 3. Diagram level guidance

The vision and epic definitions should document recommended diagram types:

| Level | Recommended diagrams |
|-------|---------------------|
| Vision | C4 Context diagram, system landscape, high-level flowchart |
| Epic | C4 Container or Component diagram, sequence diagram, data flow, detailed flowchart |

This is advisory, not enforced — any diagram satisfies the requirement.

### 4. Validation

`specwatch scan` (or a new check in `adr-check.sh`) flags architecture overviews that lack a diagram with a `ARCH_NO_DIAGRAM` warning.

## Acceptance Criteria

1. **Given** an Epic folder with an `architecture-overview.md`, **when** `specgraph scope <SPEC-under-that-epic>` runs, **then** the SUPPORTING section shows the Epic-level architecture overview path.

2. **Given** an Epic with an architecture overview AND a parent Vision with an architecture overview, **when** `specgraph scope` runs, **then** both are shown (Epic first, Vision second).

3. **Given** an architecture overview containing a mermaid code block, **when** the diagram check runs, **then** no warning is emitted.

4. **Given** an architecture overview containing an image reference, **when** the diagram check runs, **then** no warning is emitted.

5. **Given** an architecture overview with only prose (no mermaid, no image, no diagram heading), **when** the diagram check runs, **then** a `ARCH_NO_DIAGRAM` warning is emitted.

6. **Given** swain-design creating or updating an architecture overview, **when** the operator provides content, **then** the agent prompts for or generates a diagram if none is included.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Epic-level arch overview in scope output | specgraph.sh do_scope walks Epic then Vision parent chain | PASS |
| Both Epic+Vision shown when both exist | Bash specgraph walks parent chain; Python scope() walks arch_ancestor_ids | PASS |
| Mermaid block → no warning | arch_check.py has_diagram() detects mermaid; specwatch scan produces no ARCH_NO_DIAGRAM | PASS |
| Image reference → no warning | has_diagram() detects markdown + HTML img refs | PASS |
| Prose only → ARCH_NO_DIAGRAM | specwatch scan_arch_diagrams() emits ARCH_NO_DIAGRAM | PASS |
| Definition files updated | epic-definition.md + vision-definition.md updated with diagram guidance | PASS |

## Scope & Constraints

- Does not change the architecture overview file format — just where it can live and what it must contain
- Does not require any specific diagramming tool — mermaid is preferred but images are acceptable
- The diagram check is a warning, not a hard gate — existing overviews without diagrams are flagged but not blocked
- Changes touch: vision-definition.md, epic-definition.md, specgraph `scope` command, specwatch or adr-check

## Implementation Approach

1. **Update definitions (TDD):** Update vision-definition.md with diagram guidance. Update epic-definition.md to document architecture overviews as a supported supporting doc with diagram level guidance.

2. **Update specgraph scope:** Extend the architecture-overview detection to walk the parent chain (Epic first, then Vision). In the Python rewrite (SPEC-031), implement this directly. In bash, update `do_scope`.

3. **Add diagram check:** Add a function to check for mermaid blocks, image refs, or diagram headings in an architecture overview file. Wire into specwatch scan as `ARCH_NO_DIAGRAM`.

4. **Update swain-design workflow:** When creating an architecture overview, the agent should include or prompt for a diagram.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Complete | 2026-03-14 | dacbf2c | Epic-level arch overview detection, arch_check.py (15 tests), scan_arch_diagrams in specwatch, definition files updated |
