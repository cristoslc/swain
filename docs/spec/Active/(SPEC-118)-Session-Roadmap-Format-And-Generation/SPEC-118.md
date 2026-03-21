---
title: "SESSION-ROADMAP.md Format and Generation"
artifact: SPEC-118
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-039
parent-initiative: INITIATIVE-019
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SESSION-ROADMAP.md Format and Generation

## Problem Statement

No session-scoped working surface exists. The operator's reference is either the full ROADMAP.md (too broad) or ephemeral terminal output (not persistent/recoverable).

## External Behavior

**Before:** The operator works from ROADMAP.md (project-wide, not session-scoped) or relies on terminal output that is lost on context clear.

**After:** chart.sh gains a `session` subcommand that generates SESSION-ROADMAP.md. The file contains:

1. **Evidence basis section** -- ROADMAP.md hash, focus lane ID, artifacts consulted
2. **Decision set** -- items needing operator input, filtered to focus lane
3. **Recommended Next** -- highest-leverage item by unblock score
4. **Session Goal** -- specific, bounded, ~3-5 decisions, all within focus area
5. **Progress section** -- what changed since last session, based on git diff of artifacts
6. **Decision records** -- accumulated as decisions are made: artifact ID + action + commit hash
7. **Walk-away signal** -- explicit "no more decisions needed" or "N remaining deferred to next session"

The file is committed on session close. `git log -p SESSION-ROADMAP.md` serves as a session diary.

## Acceptance Criteria

### AC1: chart.sh session generates SESSION-ROADMAP.md

**Given** the operator invokes `chart.sh session --focus INITIATIVE-005`
**When** the command completes
**Then** a SESSION-ROADMAP.md file is generated in the project root

### AC2: All 7 sections present

**Given** a generated SESSION-ROADMAP.md
**When** the file is inspected
**Then** it contains all 7 sections: evidence basis, decision set, recommended next, session goal, progress, decision records, walk-away signal

### AC3: Valid markdown

**Given** a generated SESSION-ROADMAP.md
**When** opened in any markdown viewer
**Then** it renders cleanly with no broken syntax

### AC4: Lightweight evidence pointers

**Given** the evidence basis section
**When** inspected
**Then** it uses artifact ID + commit hash pointers, not content copies

### AC5: Decision set filtered to focus lane

**Given** a focus lane of INITIATIVE-005
**When** SESSION-ROADMAP.md is generated
**Then** the decision set contains only items that are children of INITIATIVE-005

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- New `session` subcommand for chart.sh
- SESSION-ROADMAP.md file format definition
- Generation logic using existing specgraph data
- Focus lane filtering

**Out of scope:**
- Session lifecycle management (SPEC-119)
- Changes to ROADMAP.md itself (SPEC-120)
- Session detection hooks in other skills (SPEC-121)

**Constraints:**
- Evidence basis must use lightweight pointers (artifact ID + commit hash), not content copies
- File must be valid markdown that opens cleanly in any viewer
- Decision set must be filtered to the focus lane's children only

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
