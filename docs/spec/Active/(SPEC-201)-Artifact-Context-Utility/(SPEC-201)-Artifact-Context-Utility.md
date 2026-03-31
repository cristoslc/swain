---
title: "Artifact Context Utility"
artifact: SPEC-201
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: feature
parent-epic: EPIC-049
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Artifact Context Utility

## Problem Statement

Every skill that shows artifacts to the operator prints bare IDs or IDs with titles. The operator must context-switch to remember what each ID means and where it stands. There is no shared utility for producing context-rich artifact references.

## Desired Outcomes

A single script that any skill can call to get a context line for any artifact. The operator sees a meaningful title, a scope sentence, and a progress clause — the ID is present but secondary.

## External Behavior

A script (`artifact-context.sh` or Python equivalent) in `.agents/bin/`.

**Input:** One or more artifact IDs as positional arguments. Optional `--format` flag: `line` (default), `json`.

**Output (line mode):**
```
**Readability enforcement** `SPEC-203` — deterministic FK scoring for all artifacts. All 3 deliverables shipped.
```

**Output (json mode):**
```json
{
  "id": "SPEC-203",
  "title": "Readability enforcement",
  "scope": "deterministic FK scoring for all artifacts",
  "progress": "All 3 deliverables shipped.",
  "status": "Active"
}
```

**Data sources (in priority order):**
1. Frontmatter `title` field → plain-language title
2. First sentence of `## Problem Statement` or `## Goal` or `## Goal / Objective` → scope sentence
3. `## Progress` section if it exists → progress clause
4. Specgraph child artifact counts as fallback → "3 of 5 child specs complete"
5. Artifact `status` from frontmatter → used when no progress data exists ("Active, no work started")

**Display convention:**
- Title leads bold (prominent in terminal)
- ID in code font (secondary/dimmed)
- Scope and progress as plain text after em dash

## Acceptance Criteria

1. **Given** an artifact ID with a `## Progress` section, **when** the utility runs, **then** it returns a context line with title, ID, scope, and progress clause.

2. **Given** an artifact ID with no `## Progress` section but child artifacts, **when** the utility runs, **then** the progress clause falls back to child artifact counts.

3. **Given** an artifact ID with no progress and no children, **when** the utility runs, **then** the progress clause shows the artifact status.

4. **Given** `--format json`, **when** the utility runs, **then** output is valid JSON with id, title, scope, progress, and status fields.

5. **Given** multiple artifact IDs, **when** the utility runs, **then** it outputs one context line per artifact.

6. **Given** an invalid artifact ID, **when** the utility runs, **then** it prints an error to stderr and continues with remaining IDs.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: the script, symlink to `.agents/bin/`, tests
- Out of scope: changing how skills call the utility (that's SPEC-202)
- No dependency on SPEC-199 or SPEC-200 — works with or without progress sections by falling back to specgraph data

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
