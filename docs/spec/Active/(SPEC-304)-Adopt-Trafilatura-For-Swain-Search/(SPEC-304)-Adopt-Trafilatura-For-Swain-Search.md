---
title: "Adopt trafilatura for main-content extraction in swain-search"
artifact: SPEC-304
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-11
last-updated: 2026-04-11
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPIKE-071
depends-on-artifacts:
  - SPIKE-071
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Adopt trafilatura for main-content extraction in swain-search

## Problem Statement

swain-search relies on the agent to strip boilerplate from fetched web pages by hand. The results vary — navs, sidebars, footers, and cookie banners leak into trove sources based on model judgment and page layout. The Gastown trove needed hand-curation of ~52KB of raw fetch output to get a clean source. [SPIKE-071](../../../research/Complete/(SPIKE-071)-Trafilatura-Content-Extraction/(SPIKE-071)-Trafilatura-Content-Extraction.md) ran four candidates head-to-head and picked trafilatura as the winner.

## Desired Outcomes

Trove sources are cleaner and more consistent. The agent spends less time on boilerplate removal and more on synthesis. Better signal-to-noise in sources means better synthesis downstream.

## External Behavior

**Inputs:** A web page URL passed to swain-search for collection.

**Outputs:** Normalized markdown with main content extracted, boilerplate removed, and metadata (title, author, date) populated from the page when available.

**Preconditions:** `uv` is available. Trafilatura is installable via `uv run --with trafilatura`.

**Constraints:** No persistent Python dependency added to the project. Trafilatura runs as a one-shot via `uv run`.

## Acceptance Criteria

1. **Given** a web page URL, **when** swain-search collects it, **then** trafilatura extracts main content before normalization.
2. **Given** a page with nav, sidebar, and footer, **when** extracted, **then** none of those appear in the normalized source.
3. **Given** a page with title and date, **when** extracted, **then** frontmatter fields are filled from trafilatura's metadata. The author field is advisory — SPIKE-071 showed it can latch onto wrong data. The agent may override it later.
4. **Given** a page where trafilatura fails or returns nothing (e.g., a listing page), **when** tried, **then** swain-search falls back to `convert_to_markdown` / `WebFetch` and logs a warning.
5. **Given** a typical web page, **when** the pipeline runs, **then** it finishes in under 10 seconds.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only web page sources change. Forum, media, repo, CLI, and local types stay the same.
- Trafilatura runs via `uv run --with trafilatura` — no `requirements.txt` or `pyproject.toml` change.
- The extraction script goes in `skills/swain-search/scripts/` per skill convention.
- A post-process step may de-dupe repeated headings (SPIKE-071 saw "Table of Contents" duplicated on one page). Keep it small.

## Implementation Approach

Per [SPIKE-071](../../../research/Complete/(SPIKE-071)-Trafilatura-Content-Extraction/(SPIKE-071)-Trafilatura-Content-Extraction.md):

1. Build `skills/swain-search/scripts/extract-content.sh`. It wraps `uv run --with trafilatura python3` and pulls main content and metadata from a URL. Output shape: YAML frontmatter (title, url, hostname, description, sitename, date) then a markdown body.
2. Update SKILL.md's web page collection step to call the script before normalization.
3. Add fallback logic: if trafilatura returns empty or errors, fall back to the `convert_to_markdown` / `WebFetch` path and log a warning.
4. Post-process: de-dupe identical consecutive headings.
5. Treat trafilatura's `author` field as advisory. The agent may override it.
6. Update `normalization-formats.md` to cover the new extraction step.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-11 | -- | Initial creation. Blocked on SPIKE-071. |
| Active | 2026-04-11 | -- | SPIKE-071 complete; trafilatura selected. SPEC unblocked and scoped. |
