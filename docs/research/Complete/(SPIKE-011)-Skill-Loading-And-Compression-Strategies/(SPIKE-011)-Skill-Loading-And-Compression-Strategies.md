---
title: "Skill Loading and Compression Strategies"
artifact: SPIKE-011
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "What strategies can reduce how much of a skill's content is loaded into context on invocation — and what are the tradeoffs of each?"
gate: Pre-EPIC-006-specs
risks-addressed:
  - Lazy-loading reference content may cause agents to miss information they need
  - Splitting SKILL.md may break skill routing or invocation mechanics
  - Some content looks like documentation but is actually behavioral — removing it changes agent behavior silently
depends-on: []
linked-artifacts:
  - EPIC-006
  - SPIKE-010
evidence-pool: ""
---

# Skill Loading and Compression Strategies

## Question

What strategies can reduce how much of a skill's content is loaded into context on invocation — and what are the tradeoffs of each?

## Go / No-Go Criteria

**Go:** At least one strategy is identified that can reduce total loaded content by ≥50% for the largest skills without requiring runtime changes to Claude Code's skill loading mechanism.

**No-Go:** No reduction strategy can achieve meaningful savings without either removing behavioral content or requiring changes outside the swain skill boundary.

## Pivot Recommendation

If no-go on in-band strategies: investigate whether Claude Code's `@file` include pattern or similar can be used to load reference material only when a specific sub-workflow is invoked.

## Findings

**Verdict: GO** — Content externalization (Strategy A) alone achieves 48-55% reduction for the top 3 skills. Combined with compression and deduplication, 58-61% reduction is projected.

### Key constraint

Claude Code loads SKILL.md as a single complete file. There is no `@file` include or conditional section loading within SKILL.md. The `@file` mechanism only works in CLAUDE.md/AGENTS.md. Reference files in `references/` require explicit Read tool calls.

### Strategy comparison

| Strategy | Est. savings (top 3) | Feasibility | Risk | CC changes? |
|----------|---------------------|-------------|------|-------------|
| **A: Externalization** | 48-55% | HIGH | MEDIUM | None |
| **B: Compression** | 15-25% | HIGH | MEDIUM | None |
| **C: Conditional loading** | 30-40% per op | LOW-MEDIUM | HIGH | None (workaround via splitting) |
| **D: Deduplication** | 3-5% global | HIGH | LOW | None |

### Recommended approach: A + B + D (skip C)

1. **A (externalization)** — primary lever. Move to `references/`:
   - Conditional workflows (superpowers, evidence pools, GitHub Issues integration)
   - Detailed bash procedures (doctor's platform/legacy cleanup)
   - Reference tables and diagrams (ER model, tool availability, anti-rationalization)
   - Methodology sections (TDD enforcement, escalation triage)

2. **B (compression)** — secondary pass on remaining content:
   - Tighten prose to imperative instructions
   - Remove obvious "if not found, skip" branches
   - Collapse multi-step bash to single representative examples

3. **D (deduplication)** — cleanup:
   - Session bookmark sections (6 copies) → one-line directives
   - Settings reading, script location patterns → inline-reduce

4. **Skip C** — skill splitting adds routing complexity and skill proliferation (14 → 25-30) without justification when A+B hit the target.

### Projected outcomes

| Skill | Current tokens | After A+B+D | Reduction |
|-------|---------------|-------------|-----------|
| swain-design | 6,319 | ~2,625 | ~58% |
| swain-doctor | 5,509 | ~2,125 | ~61% |
| swain-do | 5,019 | ~2,000 | ~60% |

### Risk mitigations

- **Agent misses externalized content:** SKILL.md pointers say "Read X before doing Y" — proven pattern (swain-do line 17: "Before first use: Read tk-cheatsheet.md")
- **Compression loses nuance:** Keep critical behavioral rules in SKILL.md; only move procedural details and lookup tables
- **Extra Read calls add latency:** One additional call per operation is negligible vs. existing tool call patterns

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
| Complete | 2026-03-13 | 459bdc7 | GO — A+B+D strategy, 58-61% reduction projected |
