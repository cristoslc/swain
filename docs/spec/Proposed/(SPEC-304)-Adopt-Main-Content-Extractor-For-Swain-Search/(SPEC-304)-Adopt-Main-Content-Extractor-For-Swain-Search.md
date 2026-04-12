---
title: "Adopt a main-content extractor for swain-search"
artifact: SPEC-304
track: implementable
status: Proposed
author: Cristos L-C
created: 2026-04-11
last-updated: 2026-04-11
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPIKE-069
depends-on-artifacts:
  - SPIKE-069
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Adopt a main-content extractor for swain-search

## Problem Statement

swain-search relies on the agent to strip boilerplate from fetched web pages by hand. The results vary — navs, sidebars, footers, and cookie banners leak into trove sources based on model judgment and page layout. The Gastown trove (just created) needed manual curation of ~52KB of raw fetch output to get a clean source.

## Desired Outcomes

Trove sources are cleaner and more consistent. The agent spends less time on boilerplate removal and more on synthesis. Better signal-to-noise in sources means better synthesis downstream.

## External Behavior

**Inputs:** A web page URL passed to swain-search for collection.

**Outputs:** Normalized markdown with main content extracted, boilerplate removed, and metadata (title, author, date) populated from the page when available.

**Preconditions:** `uv` is available. The chosen extractor package is installable via `uv run --with`.

**Constraints:** No persistent Python dependency added to the project. The extractor runs as a one-shot via `uv run`. The extractor is whichever candidate SPIKE-069 names as the winner.

## Acceptance Criteria

1. **Given** a web page URL, **when** swain-search collects it, **then** the SPIKE-069 winner extracts main content before normalization.
2. **Given** a page with nav, sidebar, and footer, **when** extracted, **then** none of those appear in the normalized source.
3. **Given** a page with title, author, and date, **when** extracted, **then** frontmatter fields are filled from the extractor's metadata.
4. **Given** a page where the extractor fails or returns nothing, **when** tried, **then** swain-search falls back to `convert_to_markdown` / `WebFetch` and logs a warning.
5. **Given** a typical web page, **when** the pipeline runs, **then** it finishes in under 10 seconds.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only web page sources change. Forum, media, repo, CLI, and local types stay the same.
- The extractor runs via `uv run --with <pkg>` — no `requirements.txt` or `pyproject.toml` change.
- The extraction script goes in `skills/swain-search/scripts/` per skill convention.
- Library choice is fixed by SPIKE-069. If that spike concludes "stay on current path", this SPEC is closed as Abandoned.

## Implementation Approach

Blocked on [SPIKE-069](../../../research/Active/(SPIKE-069)-Trafilatura-Content-Extraction/(SPIKE-069)-Trafilatura-Content-Extraction.md) findings. Rough shape:

1. Create `skills/swain-search/scripts/extract-content.sh` that wraps `uv run --with <winner> python3 -c "..."` to extract main content and metadata from a URL.
2. Update SKILL.md's web page collection step to call the extraction script before normalization.
3. Add fallback logic: if the extractor returns empty/error, proceed with existing path.
4. Update `normalization-formats.md` to document the new extraction step.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-11 | -- | Initial creation. Blocked on SPIKE-069. |
