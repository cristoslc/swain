---
title: "Absorb swain-status into swain-session"
artifact: SPEC-122
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-039
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPEC-118
  - SPEC-169
  - SPEC-170
  - SPEC-123
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Absorb swain-status into swain-session

## Problem Statement

swain-status and swain-session are separate skills with overlapping concerns. swain-status produces a dashboard; swain-session manages session state. The new session lifecycle makes swain-status redundant -- its valuable outputs (decisions, recommendations, focus lane) are absorbed into SESSION-ROADMAP.md and ROADMAP.md.

## External Behavior

**Before:** swain-status is a separate skill that produces a dashboard, handles "what's next" queries, scans GitHub issues, queries tk tasks, and manages a cache. swain-session only manages tab names and bookmarks.

**After:**
- swain-status skill is deprecated and removed
- Its SKILL.md routing entries redirect to swain-session
- "what's next", "status", "dashboard" trigger swain-session, which opens SESSION-ROADMAP.md (or starts a new session if none exists)
- The swain-status.sh script's unique logic (GitHub issue scanning, tk task queries, cache management) is either migrated to swain-session or dropped if redundant with SESSION-ROADMAP
- MOTD compact output is preserved as a swain-session feature

## Acceptance Criteria

### AC1: swain-status skill directory removed

**Given** the migration is complete
**When** the skill directory structure is inspected
**Then** the swain-status skill directory no longer exists

### AC2: Trigger phrases route to swain-session

**Given** the operator says "what's next", "status", or "dashboard"
**When** the swain router processes the request
**Then** it routes to swain-session

### AC3: No functionality regression

**Given** everything swain-status previously provided
**When** the operator uses swain-session + SESSION-ROADMAP.md + ROADMAP.md
**Then** all previously available information is accessible

### AC4: MOTD compact mode preserved

**Given** swain-session is invoked in MOTD mode
**When** it generates output
**Then** the compact status output is preserved

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Removal of swain-status skill directory
- Migration of unique swain-status logic to swain-session
- Update swain router routing table
- Update AGENTS.md routing references
- Preserve MOTD compact output

**Out of scope:**
- SESSION-ROADMAP.md format (SPEC-118)
- Session lifecycle (SPEC-169)
- ROADMAP.md changes (SPEC-170)

**Constraints:**
- No functionality regression -- every output swain-status provided must be available through the new surface
- MOTD compact mode must continue to work
- Migration must be atomic -- no intermediate state where both skills exist with conflicting behavior

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
