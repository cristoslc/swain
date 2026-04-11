---
title: "Evaluate trafilatura for main content extraction in swain-search"
artifact: SPIKE-069
track: container
status: Active
author: Cristos L-C
created: 2026-04-11
last-updated: 2026-04-11
question: "Should swain-search use trafilatura for web content extraction? Would it produce cleaner output than the current approach?"
gate: Pre-MVP
risks-addressed:
  - "Boilerplate leaks into trove sources and degrades synthesis."
  - "Agent-driven content stripping varies across page layouts."
evidence-pool: ""
---

# Evaluate trafilatura for main content extraction in swain-search

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Should swain-search use trafilatura for web content extraction? Would it produce cleaner output than the current approach?

### Context

swain-search fetches web pages through two tools:

1. `convert_to_markdown` MCP tool (Dockerized, opaque internals).
2. `WebFetch` built-in tool (fetches HTML, converts to markdown via a small model).

Both return raw markdown with navigation, sidebars, footers, and cookie banners mixed in. The skill file tells the agent to "strip boilerplate" during normalization — but this is manual, uneven, and varies by model.

[Trafilatura](https://github.com/adbar/trafilatura) is a Python library built for web content extraction. It finds the main content area, strips boilerplate, and pulls metadata. It powers several academic web corpora projects and is widely used in NLP pipelines.

## Go / No-Go Criteria

1. **Content quality:** Test on 5 diverse pages (blog, docs, forum, news, digital garden). Trafilatura must have fewer boilerplate artifacts than `convert_to_markdown`.
2. **Metadata:** Must pull title, author, and date from pages that have them.
3. **Integration:** Must run via `uv run --with trafilatura` with no added dependency. Under 10 seconds per page.
4. **Markdown output:** Must preserve headings, code blocks, and tables — natively or with a light post-process step.

## Pivot Recommendation

If trafilatura fails the gate: try [readability-lxml](https://github.com/buriy/python-readability) or [newspaper3k](https://github.com/codelucas/newspaper) as lighter options. If all fail, improve the current agent-driven stripping with a prompt template and validation step.

## Findings

Results of the investigation (populated during Active phase).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-11 | -- | Initial creation. |
