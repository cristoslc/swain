---
title: "Semantic Topic Matching in Trove Prior Art Check"
artifact: SPEC-171
track: implementable
status: Complete
author: cristos
created: 2026-03-25
last-updated: 2026-03-25
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - RETRO-2026-03-25-trove-misrouting
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Semantic Topic Matching in Trove Prior Art Check

## Problem Statement

swain-search's prior art check only searches existing troves by literal keyword (grep for the source name/URL). When a new source uses different vocabulary for the same concept (e.g., "Cog" vs. "agent memory systems"), the check fails to find the matching trove. This leads to standalone troves being created when the source should extend an existing trove — causing fragmented research, rework, and wasted commits.

## Desired Outcomes

Operators get correctly routed trove placement on the first attempt. Sources about agent memory systems land in the `agent-memory-systems` trove regardless of what the source calls itself. The prior art check catches topic-level matches, not just name-level matches.

## External Behavior

**Current behavior:** Prior art check runs `grep -rl "<keyword>" docs/troves/*/manifest.yaml` where `<keyword>` is derived from the source name or URL. Misses topic-level matches.

**New behavior:** Prior art check runs in two phases:

1. **Phase 1 — Literal match** (existing): grep for source name, URL fragments, and author name against manifest files and source content. Same as today.

2. **Phase 2 — Semantic topic match** (new): After fetching the source and understanding what it's about, search existing trove tags and synthesis summaries for topic overlap:
   - Grep trove tags in manifest.yaml files for topic keywords derived from the source's *content* (not just its name)
   - Grep synthesis.md files for topic keywords
   - Report any matches with trove ID, matching tags, and source count

3. **Forced decision gate**: Before proceeding to Create mode, output a visible decision:
   > "Existing troves checked: found N potential matches: [trove-id-1 (tags: x, y), trove-id-2 (tags: a, b)]. Extending [trove-id] / Creating new trove [slug] because [reason]."

   If no matches: `"No existing troves match topic. Creating new trove [slug]."`

## Acceptance Criteria

1. **Given** a source about agent memory systems named "Cog", **when** swain-search runs the prior art check, **then** it finds the `agent-memory-systems` trove via tag match on `agent-memory`, `memory-architecture`, or `claude-code`.

2. **Given** Phase 1 finds no literal matches, **when** Phase 2 runs, **then** it searches trove tags and synthesis content using topic keywords derived from the source's content (not just its name/URL).

3. **Given** Phase 2 finds one or more matching troves, **when** the decision gate runs, **then** it outputs the match list with trove IDs and matching tags before proceeding.

4. **Given** no matches in either phase, **when** the decision gate runs, **then** it outputs "No existing troves match topic" and proceeds to Create mode.

5. **Given** the source content has not yet been fetched (URL-only invocation), **when** Phase 2 would run, **then** it uses whatever topic information is available from the URL/title (e.g., README keywords from a GitHub repo page) and defers full topic matching until after the source is fetched.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Cog → finds agent-memory-systems via tag match | SKILL.md:59 — explicit example with Cog and topic keywords `agent-memory`, `memory-architecture`, `claude-code` | Pass |
| AC2: Phase 2 searches tags/synthesis using content-derived keywords | SKILL.md:47-59 — instructions to extract 3-5 topic keywords, grep manifests and synthesis | Pass |
| AC3: Decision gate outputs match list with trove IDs and tags | SKILL.md:63-70 — template with match counts, trove IDs, tags, and routing decision | Pass |
| AC4: No matches → "No existing troves match topic" | SKILL.md:68 — decision gate template covers no-match case | Pass |
| AC5: URL-only invocation defers full topic matching | SKILL.md:61-62 — defers until source is fetched | Pass |

## Scope & Constraints

- Changes are limited to the swain-search skill file (`.claude/skills/swain-search/SKILL.md`)
- No new scripts or tooling — this is instruction-level guidance for the agent
- Phase 2 keywords are derived by the agent from reading the source content, not from an external NLP tool
- The decision gate is a visible output in the conversation, not a blocking prompt — the agent still decides, but the decision is auditable

## Implementation Approach

Single change to the "Prior art check" section of swain-search's SKILL.md:

1. After the existing Phase 1 grep commands, add Phase 2 instructions:
   - "After understanding what the source is about, extract 3-5 topic keywords from the source content"
   - "Search trove tags: `grep -l '<keyword1>\|<keyword2>' docs/troves/*/manifest.yaml`"
   - "Search synthesis summaries: `grep -l '<keyword1>\|<keyword2>' docs/troves/*/synthesis.md`"

2. Add the forced decision gate after both phases complete:
   - Template for the visible output
   - Rule: if any trove matches on 2+ topic keywords, default to Extend mode and explain why

3. Reorder the skill flow so Phase 2 runs after the source is fetched/understood (move the prior art check to after Step 2, or split it into pre-fetch and post-fetch phases).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | | Initial creation |
| Complete | 2026-03-25 | | All ACs verified — Phase 2 semantic topic matching added to swain-search |
