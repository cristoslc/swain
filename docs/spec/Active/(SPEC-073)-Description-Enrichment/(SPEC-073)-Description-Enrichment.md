---
title: "Description enrichment"
artifact: SPEC-073
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Description enrichment

## Problem Statement

12 of 18 swain skills have description word counts under the 50-word recommended minimum. Thin descriptions cause under-triggering — the skill exists but agents don't invoke it because the routing signal is too weak. Conversely, swain-do at 103 words is over-long for routing. The audit identified specific missing trigger phrases for each skill.

## External Behavior

Every swain skill's `description` frontmatter field is 50-150 words, includes concrete trigger phrases users would actually say, and avoids overly broad terms that cause false triggering.

## Acceptance Criteria

**AC-1:** Every skill's description is between 50-150 words.

**AC-2:** Each description includes at least 3 concrete trigger phrases (e.g., "configure git signing", "set up SSH keys").

**AC-3:** swain-do description trimmed to ~70 words with routing-specific content moved to body.

**AC-4:** swain-doctor description accurately reflects conditional invocation (not "ALWAYS").

**AC-5:** No description uses overly broad bare triggers ("status", "help") without qualification.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Word count of each description field | |
| AC-2 | Manual review of trigger phrases | |
| AC-3 | swain-do description word count | |
| AC-4 | swain-doctor description text | |
| AC-5 | Review for unqualified broad triggers | |

## Scope & Constraints

**In scope:** The `description` field in frontmatter of all 18 SKILL.md files. Specific suggestions are in the audit at `docs/audits/2026-03-18-skill-audit.md`.

**Out of scope:** Changing skill body content, skill logic, or operational behavior. This is metadata-only.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit theme #2: thin descriptions |
