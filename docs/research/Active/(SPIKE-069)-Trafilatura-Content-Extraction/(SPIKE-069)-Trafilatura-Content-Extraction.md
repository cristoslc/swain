---
title: "Pick the best main-content extractor for swain-search"
artifact: SPIKE-069
track: container
status: Active
author: Cristos L-C
created: 2026-04-11
last-updated: 2026-04-11
question: "Which main-content extractor best fits swain-search? Compare trafilatura, readability-lxml, newspaper3k, and the current path head-to-head."
gate: Pre-MVP
risks-addressed:
  - "Boilerplate leaks into trove sources and degrades synthesis."
  - "Agent-driven content stripping varies across page layouts."
evidence-pool: ""
---

# Pick the best main-content extractor for swain-search

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Which main-content extractor best fits swain-search? Compare trafilatura, readability-lxml, newspaper3k, and the current path head-to-head.

### Context

swain-search fetches web pages through two tools:

1. `convert_to_markdown` MCP tool (Dockerized, opaque internals).
2. `WebFetch` built-in tool (fetches HTML, converts to markdown via a small model).

Both return raw markdown with navigation, sidebars, footers, and cookie banners mixed in. The skill file tells the agent to "strip boilerplate" during normalization — but this is manual, uneven, and varies by model. This spike finds the best replacement via head-to-head comparison, not the first option that passes a bar.

## Candidates

All candidates are evaluated against the same test corpus and scoring rubric. No candidate gets a default position.

1. **[Trafilatura](https://github.com/adbar/trafilatura)** — Python library built for web content extraction. Finds main content, strips boilerplate, pulls metadata. Powers several academic web corpora projects.
2. **[readability-lxml](https://github.com/buriy/python-readability)** — Python port of Arc90's Readability algorithm. Lighter than trafilatura; focused on article extraction.
3. **[newspaper3k](https://github.com/codelucas/newspaper)** — Python library aimed at news articles. Includes metadata, author, and date extraction.
4. **Current path (baseline)** — `convert_to_markdown` or `WebFetch` plus agent-driven boilerplate stripping.

Add other candidates if they surface during research (e.g., `goose3`, `dragnet`, `boilerpy3`, `jusText`, Mozilla Readability via a Node shim).

## Evaluation Rubric

Score each candidate on the same test corpus:

- **Test corpus:** 5 diverse pages (blog, docs, forum, news, digital garden). Same URLs for all candidates.
- **Content quality:** Count boilerplate artifacts (nav, sidebar, footer, cookie banner remnants) in the output. Fewer is better.
- **Metadata:** Title, author, and date extracted correctly — yes or no per field per page.
- **Markdown fidelity:** Headings, code blocks, and tables preserved in output. Score per feature per page.
- **Runtime:** Wall-clock seconds per page.
- **Integration cost:** Lines of glue code needed to fit swain-search's normalization format. Lower is better.
- **Install footprint:** Size and dependency count when run via `uv run --with <pkg>`.

## Go / No-Go Criteria

The winner is the candidate with the best combined score across the rubric. The spike completes when:

1. All candidates have run against the full test corpus.
2. Scores are recorded in a comparison table under Findings.
3. One candidate is named the winner with reasoning, or — if no candidate clearly beats the baseline — the spike concludes "stay on the current path" with evidence.

## Pivot Recommendation

If no library beats the baseline: improve the agent-driven stripping path with a structured prompt template and validation step, rather than adding a new dependency.

## Findings

Results of the investigation (populated during Active phase).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-11 | -- | Initial creation. |
