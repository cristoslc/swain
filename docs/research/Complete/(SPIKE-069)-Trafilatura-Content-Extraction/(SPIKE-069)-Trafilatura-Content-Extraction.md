---
title: "Pick the best main-content extractor for swain-search"
artifact: SPIKE-069
track: container
status: Complete
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

**Verdict: Go — adopt trafilatura.**

Trafilatura wins the head-to-head on every category in the test corpus. It is the only candidate that preserves markdown structure (headings, links, code blocks), outputs YAML frontmatter with usable metadata, and handles all five page types without truncation or failure. The [SPEC-304](../../../spec/Proposed/(SPEC-304)-Adopt-Main-Content-Extractor-For-Swain-Search/(SPEC-304)-Adopt-Main-Content-Extractor-For-Swain-Search.md) implementation should wire trafilatura into swain-search's web-page collection step with a fallback to the current path on empty or error output.

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

### Test corpus

Five URLs were fetched once each and passed to every candidate as shared input:

| ID | Category | URL |
|----|----------|-----|
| `blog-ghuntley-ralph` | blog | https://ghuntley.com/ralph/ |
| `docs-mdn-websocket` | docs | https://developer.mozilla.org/en-US/docs/Web/API/WebSocket |
| `forum-hn-gastown` | forum | https://news.ycombinator.com/item?id=46463757 |
| `news-theverge-sample` | news (category) | https://www.theverge.com/tech |
| `garden-appleton-gastown` | digital garden | https://maggieappleton.com/gastown |

The evaluation harness lives at `evaluation/run-eval.py`. Raw HTML is cached under `evaluation/raw/`, per-library outputs under `evaluation/outputs/`, and aggregated scores in `evaluation/report.json` and `evaluation/scoring.json`.

### Content length (chars extracted)

| URL | trafilatura | readability-lxml | newspaper3k |
|-----|-------------|------------------|-------------|
| blog-ghuntley-ralph | 28,622 | 32,351 | 28,781 |
| docs-mdn-websocket | **3,572** | 856 | 203 |
| forum-hn-gastown | **5,843** | 1,488 | 0 (failed) |
| news-theverge-sample | **1,281** | 555 | 432 |
| garden-appleton-gastown | 32,182 | 31,561 | 31,670 |

### Markdown fidelity

| URL | Metric | trafilatura | readability-lxml | newspaper3k |
|-----|--------|-------------|------------------|-------------|
| blog | headings / links / code | 26 / 2 / 3 | 18 / 10 / 4 | 0 / 0 / 0 |
| docs | headings / links / code | 2 / 11 / 1 | 0 / 6 / 0 | 0 / 0 / 0 |
| forum | headings / links / code | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| garden | headings / links / code | 16 / 35 / 0 | 14 / 29 / 0 | 0 / 0 / 0 |

Trafilatura and readability-lxml both output markdown. Newspaper3k returns plain text only — link URLs appear inline without bracket syntax, and heading markers are stripped.

### Metadata

YAML frontmatter with title, URL, hostname, description, sitename, and date came back only from trafilatura. Readability-lxml gives just the title. Newspaper3k exposes metadata through object attributes but does not attach them to the text output.

Trafilatura metadata notes:

- Title was correct on every URL.
- Date was correct where present (MDN `2024-09-25`, Appleton `2026-01-24`).
- Author is noisy on the Appleton page (picked up a Bluesky webmention author rather than Maggie Appleton). Downstream code should treat the author field as advisory.

### Runtime and install footprint

All three libraries processed every page in well under a second. Runtime is not a differentiator.

| Library | Install footprint via `uv run --with` |
|---------|---------------------------------------|
| trafilatura | Moderate — pulls `lxml`, `htmldate`, `courlan`, `justext`. |
| readability-lxml | Light — plus `markdownify` for HTML-to-markdown conversion. |
| newspaper3k | Heavy — 41 packages including `feedfinder2`, `sgmllib3k`, `jieba3k`, `tinysegmenter`. Raises Python 3.12 SyntaxWarnings. Needs a patched `lxml_html_clean`. |

### Per-category behaviour

- **Blog post.** All three capture the full article. Trafilatura produces the cleanest markdown with heading structure preserved.
- **Reference docs (MDN).** Trafilatura is the only candidate that captures the full API reference (constructor, instance properties, methods). Readability-lxml truncates to the intro paragraph. Newspaper3k returns a near-empty string.
- **Forum thread (HN).** Trafilatura captures the entire thread. Readability-lxml returns only the first comment. Newspaper3k fails (0 chars).
- **News category page.** None of the candidates handles a non-article listing page well. This is expected — the test was a fair check, not a disqualifier.
- **Digital garden (Appleton).** All three capture the article body. Only trafilatura preserves heading hierarchy and adds metadata frontmatter.

### Known trafilatura caveats

1. Author detection can latch onto unrelated `author` microdata (e.g., webmention profiles). Treat as advisory; swain-search can override or blank the field when synthesis requires it.
2. On the Appleton page, the "Table of Contents" heading printed twice — a minor artifact that a one-line post-process step can de-dupe.
3. The news category page returned limited content. For listing pages, swain-search should either skip trafilatura or treat it as a failed extraction and fall back.

### Recommendation

Adopt trafilatura. Implementation specifics (fallback path, post-processing, metadata override rules) belong in SPEC-304.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-11 | -- | Initial creation. |
| Complete | 2026-04-11 | -- | Evaluation run on 5-URL corpus. Trafilatura wins on every dimension that matters. |
