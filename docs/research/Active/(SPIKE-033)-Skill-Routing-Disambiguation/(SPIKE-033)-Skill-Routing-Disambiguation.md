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
evidence-pool: ""
---

# Skill Routing Disambiguation

## Summary

## Question

How should the swain meta-router handle ambiguous user intents that match multiple sub-skills, and what disambiguation mechanisms exist in Claude Code's skill system?

## Go / No-Go Criteria

- **Go:** A disambiguation strategy exists that can be implemented in the meta-router SKILL.md without exceeding 50 lines of additional instructions, reduces misroutes by >50% on a test set of 20 ambiguous queries.
- **No-Go:** All viable strategies either require changes to the Claude Code skill system itself, or add so much routing complexity that the meta-router becomes a bottleneck.

## Pivot Recommendation

If no in-skill disambiguation is viable, recommend merging the most-confused skill pairs (e.g., fold swain-help question mode into swain-design) and document the rationale as an ADR.

## Findings

Investigate:

1. **Current overlap map:** Which skill pairs share trigger phrases? The audit identified:
   - swain-help "how do I" / "what is" overlaps with swain-design and swain-do
   - swain-status "status" / "progress" overlaps with git-native concepts
   - swain-dispatch "offload work" overlaps with general delegation
   - swain-help "I want to plan a new feature" could fire swain-design

2. **Claude Code routing internals:** How does Claude Code select between skills when multiple match? Is there a priority/score mechanism? Can skills declare conflicts or precedence?

3. **Disambiguation patterns in the wild:** How do other skill ecosystems (VS Code extensions, Slack apps, Discord bots) handle command disambiguation?

4. **Candidate strategies:**
   - Priority ordering in the routing table (first match wins)
   - Keyword exclusion lists per skill (e.g., swain-help excludes "create", "write", "build")
   - Two-pass routing: meta-router proposes a match, then asks user to confirm if confidence is low
   - Intent classification heuristics in the routing table

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit finding: no disambiguation guidance in meta-router |
