---
title: "Source Quality Ranking for swain-search"
artifact: SPEC-317
track: implementable
status: Active
author: cristos
created: 2026-04-16
last-updated: 2026-04-16
priority-weight: high
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - SPEC-001
  - SPEC-155
  - SPEC-304
  - SPIKE-072
depends-on-artifacts:
  - SPEC-304
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Source Quality Ranking for swain-search

## Problem Statement

swain-search treats every source as equally credible. Web search results are full of SEO content mills, LLM-written listicles, and sites that repackage primary sources. The skill picks the "top 3-5 most relevant results" and trusts the search engine ranking. But search engines rank for clicks, not authority. Troves fill up with low-value secondary sources. Primary sources — specs, papers, official docs, first-hand accounts — get buried. Synthesis quality suffers because "points of agreement" echo what content mills repeat, not what is true.

The [slop-creep](../../troves/slop-creep/manifest.yaml) trove documents this pattern. Effort asymmetry makes production cheap and verification expensive. Low-cost secondary sources flood the signal space. swain-search has no defense against this today.

## Desired Outcomes

Researchers get troves where primary and authoritative sources rank above SEO-driven secondary ones. The quality signal lives in the manifest. Synthesis uses it. The operator can audit it later. At a glance, you can see which sources carry weight and which are likely paraphrase.

## External Behavior

**Inputs:** A web search result set or a list of candidate URLs for trove collection.

**Outputs:**
1. A `quality-tier` field on each manifest source entry: `primary`, `secondary`, or `aggregator`.
2. A `quality-score` field: integer 1-5, derived from tier plus domain signals.
3. Synthesis generation that prefers higher-quality sources when building "key findings" and "points of agreement."
4. A `quality-rank.md` reference file in the skill directory that scores can be checked against.

**Preconditions:** swain-search is invoked in Create or Extend mode with web sources.

**Postconditions:** Every source in the manifest has a `quality-tier` and `quality-score`. Synthesis cites primary sources before secondary ones when multiple sources make the same claim.

**Constraints:** Ranking must be deterministic. Same URL, same tier. No extra network calls beyond the initial fetch. Sources are never rejected — only ranked. Operators can override any score by editing the manifest.

## Acceptance Criteria

1. **Given** a web search result set, **when** swain-search selects sources for collection, **then** each selected source receives a `quality-tier` of `primary`, `secondary`, or `aggregator` in its manifest entry.

2. **Given** a source whose hostname appears in `quality-rank.md` as a known primary domain (e.g., `developer.mozilla.org`, `spec.whatwg.org`, `arxiv.org`), **when** swain-search collects it, **then** it receives `quality-tier: primary`.

3. **Given** a source whose hostname appears in `quality-rank.md` as a known aggregator (e.g., `medium.com`, `dev.to`, `geeksforgeeks.org`, `freecodecamp.org`), **when** swain-search collects it, **then** it receives `quality-tier: aggregator`.

4. **Given** a source whose hostname is not in `quality-rank.md`, **when** swain-search collects it, **then** it receives `quality-tier: secondary` (the default) and an advisory `quality-score` of 3.

5. **Given** a source with `quality-tier: primary`, **when** score is computed, **then** it gets 5. Secondary gets 3. Aggregator gets 1.

6. **Given** a secondary source with byline metadata (author name or date) in its content, **when** score is computed, **then** it gets +1 (to 4).

7. **Given** an aggregator that links to a primary source, **when** swain-search spots the link, **then** the manifest entry gets `primary-ref: <url>` pointing to that source.

8. **Given** multiple sources making the same claim in synthesis, **when** swain-search builds the synthesis, **then** it cites the top-scoring source first. Lower sources get "also reported by."

9. **Given** a trove manifest, **when** the operator runs `trovewatch.sh scan`, **then** it shows a quality summary like "N primary, M secondary, K aggregator."

10. **Given** a manifest entry where the operator edited `quality-tier` or `quality-score`, **when** refresh runs, **then** the override stays. Refresh does not overwrite it.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC 1 | `test-quality-ranking.sh` asserts `quality-tier` present on every source | |
| AC 2 | Test with a URL from MDN; assert `quality-tier: primary` | |
| AC 3 | Test with a URL from Medium; assert `quality-tier: aggregator` | |
| AC 4 | Test with an unknown hostname; assert `quality-tier: secondary`, `quality-score: 3` | |
| AC 5 | Assert score computation: primary=5, secondary=3, aggregator=1 | |
| AC 6 | Test secondary source with byline metadata; assert score=4 | |
| AC 7 | Test aggregator source that links to a primary source; assert `primary-ref` populated | |
| AC 8 | Generate synthesis from a trove with mixed tiers; assert primary cited first | |
| AC 9 | Run trovewatch on a trove; assert quality distribution in output | |
| AC 10 | Override quality-tier in manifest, refresh, assert override preserved | |

## Scope & Constraints

**In scope:**
- `quality-tier` and `quality-score` fields on manifest source entries.
- Domain-based tier registry (`quality-rank.md`).
- Byline boost for secondary sources.
- Primary-ref detection for aggregator sources.
- Synthesis ordering by source quality.
- Trovewatch quality distribution report.
- Override persistence through refresh.

**Out of scope:**
- Automated content-level quality analysis (NLP, readability scoring).
- ML-based source credibility models.
- Network-based reputation lookups (PageRank, domain authority APIs).
- Filtering or rejecting sources (rank only, never reject).
- Quality ranking for non-web sources (media, repository, local, CLI).

**Token budget:** The domain registry is a static file. Score computation is a table lookup plus at most two heuristics (byline check, primary-ref detection). No multi-pass content analysis.

## Implementation Approach

TDD cycle 1 — Domain registry and tier assignment:
- Create `skills/swain-search/references/quality-rank.md` with primary and aggregator domain tables.
- Create `skills/swain-search/scripts/quality-classify.sh`. It takes a URL, reads the registry, and outputs tier plus base score.
- Test: given a URL, script outputs correct tier.

TDD cycle 2 — Manifest integration:
- After collecting each web source, run `quality-classify.sh` on its URL.
- Write `quality-tier` and `quality-score` to the manifest entry.
- Update `manifest-schema.md` to document the new fields.
- Test: collected trove has quality fields on all web sources.

TDD cycle 3 — Byline and primary-ref heuristics:
- Byline detection: check frontmatter for `author` or `date` fields (from trafilatura per [SPEC-304](../(SPEC-304)-Adopt-Trafilatura-For-Swain-Search/(SPEC-304)-Adopt-Trafilatura-For-Swain-Search.md)). Boost secondary score by +1.
- Primary-ref detection: scan content for links matching primary domains. Set `primary-ref` in manifest if found.
- Test both heuristics.

TDD cycle 4 — Synthesis ordering:
- Update SKILL.md Step 4 to sort sources by `quality-score` descending when building themed sections. Cite primary first. Note secondary/aggregator as "also reported by."
- Test: synthesis respects quality ordering.

TDD cycle 5 — Trovewatch and refresh:
- Add quality distribution line to `trovewatch.sh scan` output.
- On refresh, skip re-scoring sources with operator overrides. Re-score only sources without overrides.
- Test both.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-16 | — | Initial creation — operator-requested feature |