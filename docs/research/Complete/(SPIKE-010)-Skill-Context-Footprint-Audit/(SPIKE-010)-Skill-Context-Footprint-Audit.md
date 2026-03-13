---
title: "Skill Context Footprint Audit"
artifact: SPIKE-010
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which swain skills consume the most context, what content categories drive their size, and where is the waste?"
gate: Pre-EPIC-006-specs
risks-addressed:
  - Optimizing the wrong skills first — audit ensures effort targets highest-impact areas
  - Content that looks redundant may actually be load-bearing for agent behavior
depends-on: []
linked-artifacts:
  - EPIC-006
evidence-pool: ""
---

# Skill Context Footprint Audit

## Question

Which swain skills consume the most context, what content categories drive their size, and where is the waste?

## Go / No-Go Criteria

**Go:** Audit produces a ranked list of skills by token count, with each skill's content broken down by category (runtime instructions, reference tables, examples, prose). At least one clear over-specification pattern is identified.

**No-Go:** Skills are uniformly sized and all content is necessary — no meaningful reduction is possible without feature removal.

## Pivot Recommendation

If no-go: accept current footprint and close EPIC-006. If skills are large but all content is necessary, file an ADR proposing a lazy-loading mechanism instead of content trimming.

## Findings

**Verdict: GO** — Multiple clear over-specification patterns identified. ~4,000-4,500 tokens recoverable (12-14% of current SKILL.md footprint).

### Size ranking

| Rank | Skill | Bytes | Est. Tokens | % of 200k |
|------|-------|------:|------------:|----------:|
| 1 | swain-design | 25,276 | 6,319 | 3.16% |
| 2 | swain-doctor | 22,036 | 5,509 | 2.75% |
| 3 | swain-do | 20,075 | 5,019 | 2.51% |
| 4 | swain-search | 8,768 | 2,192 | 1.10% |
| 5 | swain-init | 7,617 | 1,904 | 0.95% |
| 6 | swain-release | 7,206 | 1,802 | 0.90% |
| 7 | swain-stage | 7,110 | 1,778 | 0.89% |
| 8 | swain-update | 6,543 | 1,636 | 0.82% |
| 9 | swain-session | 5,287 | 1,322 | 0.66% |
| 10 | swain-status | 4,344 | 1,086 | 0.54% |
| 11 | swain-help | 4,339 | 1,085 | 0.54% |
| 12 | swain-push | 4,016 | 1,004 | 0.50% |
| 13 | swain-keys | 3,129 | 782 | 0.39% |
| 14 | swain (router) | 1,259 | 315 | 0.16% |
| | **Total SKILL.md** | **127,005** | **31,751** | **15.88%** |
| | AGENTS.md | 7,231 | 1,808 | 0.90% |

### Top 5 waste patterns

1. **Session bookmark boilerplate duplicated 6x** (~546 tokens) — swain-design, swain-do, swain-release, swain-status, swain-push, swain-keys each carry near-identical find+invoke+format sections. Could be a one-line directive.

2. **Four-tier tracking model duplicated** (~500 tokens) — The Implementation/Coordination/Research/Reference tier table appears in both swain-design and swain-do with near-identical prose.

3. **Superpowers detection scattered across 3 skills** (~1,363 tokens) — Detection pattern (`ls .claude/skills/.../SKILL.md`) appears 3 times. Conditional behavior could be consolidated into a single reference file.

4. **Over-specified procedural bash in swain-doctor** (~1,625 tokens) — 27 code blocks totaling ~3,039 bytes of inline bash for operations the agent can infer. Platform dotfolder cleanup alone is 3,510 bytes.

5. **swain-design inlined reference material** (~1,275 tokens) — ER diagram, tooling table, lifecycle format, index maintenance rules. Purely reference content that could live in references/ (which the skill already uses for 22 other files).

### Content category breakdown (top 3 skills)

**swain-design:** 20% reference-only (could externalize), 17% conditional (superpowers/evidence pools, load on demand), 63% load-bearing runtime instructions.

**swain-doctor:** 16% platform dotfolder cleanup (over-specified bash), 12% legacy skill cleanup (over-specified bash), remainder is procedural but could be more terse.

**swain-do:** 13% escalation procedures (bash-heavy), 16% superpowers conditional, 8% first-run-only config. Core operating rules and term mapping are load-bearing.

### Well-externalized skills

swain-design is the gold standard — 22 reference files, SKILL.md uses "read [references/X]" directives. Other skills are inconsistent; swain-doctor inlines all its procedural bash rather than externalizing to scripts or reference files.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
| Complete | 2026-03-13 | — | GO — 5 waste patterns identified, ~4k-4.5k tokens recoverable |
