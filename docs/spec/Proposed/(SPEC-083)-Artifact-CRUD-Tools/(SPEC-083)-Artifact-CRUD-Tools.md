---
title: "Artifact CRUD Tools"
artifact: SPEC-083
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts:
  - SPEC-082
acceptance-criteria:
  - "`artifact_list` returns artifacts filtered by type, status, and/or parent reference"
  - "`artifact_read` returns full markdown content plus parsed frontmatter as structured data"
  - "`artifact_create` assigns next available number, creates directory and file with correct template"
  - "`artifact_update` modifies frontmatter fields and updates last-updated date"
  - All tools validate inputs and return clear error messages
  - SQLite index stays in sync with filesystem (write-through)
swain-do: required
linked-artifacts:
  - SPEC-082
  - SPEC-084
  - SPEC-085
  - SPEC-088
  - SPEC-090
---

# Artifact CRUD Tools

## Context

Core tools for reading, listing, and creating artifacts. These are the most-used operations across all swain workflows. Every agent interaction with the artifact corpus — whether checking status, drafting a new spec, or updating a field — routes through these tools. Building them on top of the SPEC-082 SQLite scaffold means queries are fast and writes are durable across server restarts.

## Scope

**In scope:**
- `artifact_list`: filter artifacts by type, status, and/or parent reference; returns list of matches with key fields
- `artifact_read`: given an artifact ID or file path, return full markdown content plus parsed frontmatter as structured data
- `artifact_create`: assign next available artifact number, create the correct directory and file with proper frontmatter template and lifecycle table
- `artifact_update`: update one or more frontmatter fields; automatically sets `last-updated` to today

**Out of scope:**
- Phase transitions and directory moves (SPEC-084)
- Chart and aggregate queries (SPEC-085)

## Acceptance Criteria

- `artifact_list` returns artifacts filtered by type, status, and/or parent reference
- `artifact_read` returns full markdown content plus parsed frontmatter as structured data
- `artifact_create` assigns next available number, creates directory and file with correct template
- `artifact_update` modifies frontmatter fields and updates last-updated date
- All tools validate inputs and return clear error messages
- SQLite index stays in sync with filesystem (write-through)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
