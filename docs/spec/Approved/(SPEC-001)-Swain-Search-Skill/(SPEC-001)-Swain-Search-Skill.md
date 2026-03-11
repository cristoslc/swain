---
title: "swain-search Skill"
artifact: SPEC-001
status: Approved
author: cristos
created: 2026-03-09
last-updated: 2026-03-11
parent-epic: EPIC-001
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
swain-do: required
---

# swain-search Skill

## Problem Statement

swain-design artifacts (spikes, ADRs, visions, epics) often need structured research inputs, but there's no standardized way to collect, normalize, cache, and share source materials. Research is ad-hoc, duplicated across related artifacts, and lacks provenance tracking.

## External Behavior

### Inputs

The skill accepts a mix of source types:

- **Web search queries** — searches the web, normalizes top results
- **URLs** — web pages, forum threads, documentation
- **Video/audio URLs** — transcribed and normalized
- **Local file paths** — PDFs, documents, existing markdown
- **Pool ID** — reference an existing pool to refresh or extend

Plus context:
- **Pool ID** (slug) — required, identifies the evidence pool
- **Tags** — for discovery by other artifacts
- **Freshness TTL** — optional override per source type

### Outputs

An evidence pool at `docs/evidence-pools/<pool-id>/`:

```
docs/evidence-pools/<pool-id>/
├── manifest.yaml
├── sources/
│   ├── 001-<slug>.md
│   └── ...
└── synthesis.md
```

### Preconditions

- At least one source input (query, URL, path) provided
- Pool ID specified (or inferred from context)

### Postconditions

- All sources normalized to markdown with consistent frontmatter
- manifest.yaml tracks provenance (URL, fetch date, content hash, type)
- synthesis.md auto-generated from normalized sources
- Pool is ready to be referenced via `evidence-pool: <pool-id>@<commit-hash>`

### Capability References

The skill references generic capabilities, not specific tool names:
- "web search" — any available search capability
- "browser / page fetcher" — any capability that can retrieve and render web pages
- "media transcription" — any capability that can convert audio/video to text
- "document conversion" — any capability that can convert PDFs, DOCX, etc. to markdown

When a capability isn't available, the skill degrades gracefully:
- No web search → skip search-based sources, warn user
- No browser → fall back to basic URL fetch, or accept manual paste
- No media transcription → accept pre-made transcripts, skip auto-transcription
- No document conversion → accept pre-converted markdown

## Acceptance Criteria

1. **Given** a web search query, **when** swain-search runs, **then** it searches, normalizes top results into `sources/`, and generates manifest entries with URLs, fetch dates, and content hashes.

2. **Given** a URL to a web page, **when** swain-search runs, **then** it fetches the page, strips boilerplate (nav, ads, sidebars), and produces a clean markdown source with title, URL, and fetch date in frontmatter.

3. **Given** a video/audio URL, **when** swain-search runs, **then** it transcribes the content and produces a markdown source with title, URL, duration, and speaker labels (when available).

4. **Given** a local file path (PDF, DOCX, etc.), **when** swain-search runs, **then** it converts to markdown and produces a source with the original path in frontmatter.

5. **Given** an existing pool ID, **when** swain-search is invoked with new sources, **then** it extends the pool (appends to manifest, adds new source files, regenerates synthesis).

6. **Given** an existing pool with stale sources (past TTL), **when** swain-search is invoked with `--refresh`, **then** it re-fetches stale web sources, compares content hashes, and only re-normalizes changed sources.

7. **Given** a pool with sources, **when** synthesis.md is generated, **then** it contains a structured distillation of key findings across all sources, organized by theme.

8. **Given** a missing capability (e.g., no web search MCP), **when** swain-search attempts to use it, **then** it warns the user and skips that source type without failing the entire run.

## Scope & Constraints

**In scope:**
- SKILL.md with skill instructions
- `references/manifest-schema.md` — manifest.yaml field definitions
- `references/normalization-formats.md` — per-source-type markdown structure
- Graceful degradation for missing capabilities

**Out of scope:**
- evidencewatch script (SPEC-002)
- swain-design integration hooks (SPEC-003)
- Semantic pool discovery (phase 2)

## Implementation Approach

1. **Manifest schema** — define manifest.yaml structure (references/manifest-schema.md)
2. **Normalization formats** — define per-type markdown structure (references/normalization-formats.md)
3. **SKILL.md** — write the skill: mode detection, source collection workflow, synthesis generation, refresh logic, graceful degradation
4. **Wire into ecosystem** — add to swain router, AGENTS.md, README

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-09 | — | Initial creation |
