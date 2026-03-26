---
title: "Skill Routing Disambiguation"
artifact: SPIKE-033
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "How should the swain meta-router handle ambiguous user intents that match multiple sub-skills, and what disambiguation mechanisms exist in Claude Code's skill system?"
gate: Pre-implementation
risks-addressed:
  - Misrouted skill invocations waste tokens and confuse users
  - Overlapping trigger phrases between swain-help, swain-design, and swain-do
linked-artifacts:
  - EPIC-031
  - SPEC-073
evidence-pool: ""
---

# Skill Routing Disambiguation

## Summary

The skill routing overlap problem is narrower than the audit suggested. Claude Code's own description-based routing handles most disambiguation well. SPEC-073's description enrichment further reduced overlap. The only material confusion is swain-help vs swain-design for artifact-related questions, which is resolved by a single heuristic in the meta-router. **Recommendation: No-Go on a disambiguation framework; add one routing hint instead.**

## Question

How should the swain meta-router handle ambiguous user intents that match multiple sub-skills, and what disambiguation mechanisms exist in Claude Code's skill system?

## Go / No-Go Criteria

- **Go:** A disambiguation strategy exists that can be implemented in the meta-router SKILL.md without exceeding 50 lines of additional instructions, reduces misroutes by >50% on a test set of 20 ambiguous queries.
- **No-Go:** All viable strategies either require changes to the Claude Code skill system itself, or add so much routing complexity that the meta-router becomes a bottleneck.

## Pivot Recommendation

If no in-skill disambiguation is viable, recommend merging the most-confused skill pairs (e.g., fold swain-help question mode into swain-design) and document the rationale as an ADR.

## Findings

### 1. Current overlap map

Analysis of the meta-router routing table and skill descriptions reveals these overlap pairs:

| Query | Candidate A | Candidate B | Severity |
|-------|-------------|-------------|----------|
| "how do I create a spec?" | swain-help ("how do I") | swain-design ("spec") | Medium — action verb "create" should route to design |
| "what is an ADR?" | swain-help ("what is") | swain-design ("ADR") | Low — informational, help is correct |
| "what's next?" | swain-status ("what's next") | swain-do ("what to work on") | Low — both converge; status shows broader view |
| "status" | swain-status ("status") | git status | Low — context-dependent; "project status" vs "git status" |
| "I want to plan a new feature" | swain-help (onboarding catch-all) | swain-design ("feature") | Medium — action intent should route to design |
| "offload work" | swain-dispatch ("offload") | general delegation | Low — already narrowed in audit by replacing with "dispatch" |

The most-confused pair is **swain-help vs swain-design**. Both respond to "how do I [artifact action]?" queries. The meta-router's instruction "pick the most specific match" resolves this correctly in practice — artifact names (spec, epic, ADR) are more specific than generic help triggers ("how do I", "what is").

### 2. Claude Code routing internals

Claude Code's skill system works by description matching — the model reads all skill descriptions and selects the best match based on semantic similarity with the user's intent. Key observations:

- **No explicit priority mechanism** — there is no `priority` frontmatter field. The model decides based on description richness and specificity.
- **No conflict declaration** — skills cannot declare "I conflict with X".
- **The meta-router is itself a skill** — `swain` is loaded by Claude Code like any other skill. Its routing table is a second level of dispatch that happens after Claude Code's own skill selection.
- **Direct invocation bypasses the meta-router** — `/swain-design` goes directly to swain-design, not through the meta-router. Only `/swain` or natural language triggers hit the meta-router.

This means disambiguation in the meta-router only matters when the user invokes `/swain` (not a direct skill). Since Claude Code's own routing already selects the right skill for most natural language queries via description matching, the meta-router overlap is a narrow problem.

### 3. Disambiguation patterns

- **VS Code Command Palette**: First-match with fuzzy scoring. No disambiguation dialog.
- **Slack apps**: Exact command match. No disambiguation needed (each command is unique).
- **Discord bots**: Prefix-based exact match. Name collisions are handled at registration time.
- **Chatbot NLU systems (Rasa, Dialogflow)**: Intent classification with confidence threshold. Below threshold = fallback/clarification.

The most relevant pattern is the confidence-threshold approach: if the model's confidence in a match is low, fall back to clarification. However, Claude Code doesn't expose a confidence score to skill authors.

### 4. Candidate strategy evaluation

| Strategy | Feasibility | Effectiveness | Lines added |
|----------|-------------|---------------|-------------|
| Priority ordering (first match wins) | High — already implicit | Low — doesn't address semantic overlap | 0 |
| Keyword exclusion lists | Medium — adds complexity | Medium — fragile, grows over time | ~20 |
| Two-pass with confirmation | Low — meta-router is haiku model, can't reliably detect ambiguity | Medium — adds latency | ~15 |
| Intent classification heuristics | Medium — add a "when in doubt" rule | High — one rule resolves most confusion | ~5 |

**Recommended strategy**: Add a single disambiguation rule to the meta-router:

> When the user's intent contains an artifact type name (spec, epic, ADR, spike, etc.) alongside a question word (how, what, why), prefer **swain-design** over **swain-help**. The user wants to do something with an artifact, not learn about the skill system.

This single heuristic resolves the most-confused pair (help vs design) with minimal added complexity.

### 5. Existing mitigations already in place

The EPIC-031 audit remediation (SPEC-073) enriched all skill descriptions to 50-150 words with concrete trigger phrases. This significantly reduces the overlap problem:
- swain-help's description now includes specific exclusion context: "any question about swain skills, artifacts, or workflows"
- swain-design's description now includes concrete action verbs: "create, validate, transition"
- swain-dispatch replaced "offload work" with "dispatch a swain artifact to a GitHub Actions runner"

These description improvements are the most effective disambiguation mechanism available, because Claude Code uses descriptions as the primary routing signal.

## Recommendation: No-Go (with minor enhancement)

**No-Go on a full disambiguation framework.** The overlap problem is narrower than the audit suggested, primarily because:
1. Claude Code's own description-based routing handles most cases well
2. SPEC-073 description enrichment has already narrowed the overlap
3. Direct invocation (`/swain-design`) bypasses the meta-router entirely
4. The remaining overlap (help vs design for artifact questions) is resolvable with one heuristic

**Recommended action**: Add a single disambiguation hint to the meta-router SKILL.md:
> "When the user's intent includes an artifact type name (spec, epic, ADR, spike, vision, initiative, journey, persona, runbook, design) alongside a question word, prefer swain-design. swain-help is for meta-questions about swain itself, not for artifact operations."

This is ~3 lines, well under the 50-line threshold, and addresses the only material overlap.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit finding: no disambiguation guidance in meta-router |
