---
title: "Roadmap Jinja templates"
artifact: SPEC-109
track: implementable
status: Complete
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-105
  - SPEC-108
  - SPEC-110
  - SPEC-112
depends-on-artifacts:
  - SPEC-108
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Roadmap Jinja templates

## Problem Statement

All rendering is embedded in Python string concatenation in roadmap.py. Layout changes require editing Python code. Presentation concerns (Mermaid syntax, markdown table structure, legend format) are tangled with data computation.

## External Behavior

Rendering is driven by Jinja2 templates stored under `skills/swain-design/templates/roadmap/`. roadmap.py computes the data model via SPEC-108's `collect_roadmap_items()`, passes the result to Jinja2, and writes output files. Template authors can change layout and formatting without touching Python.

## Acceptance Criteria

- Templates live in `skills/swain-design/templates/roadmap/`: `quadrant.mmd.j2`, `legend.md.j2`, `eisenhower.md.j2`, `gantt.mmd.j2`, `deps.mmd.j2`, `roadmap.md.j2`
- roadmap.py computes the data model (SPEC-108), passes it to Jinja2, writes output
- Template changes do not require Python code changes
- jinja2 added as a dependency (via uv)
- Existing output format is preserved (templates produce the same markdown structure)

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

Scope is the six named templates and the roadmap.py render path. Other Python scripts are out of scope. Existing output format must be preserved; no visual regressions.

## Implementation Approach

1. Add jinja2 via `uv add jinja2`.
2. Extract each rendering section of roadmap.py into the corresponding `.j2` template.
3. Replace Python string concatenation with `jinja2.Environment` render calls.
4. Write snapshot tests comparing rendered output against the current output baseline.
5. Confirm all six templates exist and roadmap.py no longer contains inline Mermaid or markdown string assembly.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 |  | Initial creation |
| Complete | 2026-03-20 | 35b7d1d | Jinja2 templates extracted; all renderers branch on _HAS_JINJA with fallback paths |
