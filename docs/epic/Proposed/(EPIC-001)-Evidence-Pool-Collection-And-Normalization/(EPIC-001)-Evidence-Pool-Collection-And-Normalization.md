---
title: "Evidence Pool Collection and Normalization"
artifact: EPIC-001
status: Proposed
author: cristos
created: 2026-03-09
last-updated: 2026-03-09
parent-vision: ~
success-criteria:
  - swain-search skill can collect sources from web, local files, and video/audio and normalize them into a consistent markdown format
  - Evidence pools are cached in docs/evidence-pools/<pool-id>/ with manifest, normalized sources, and auto-generated synthesis
  - Multiple artifacts can reference the same pool via evidence-pool frontmatter with commit-hash pinning
  - evidencewatch script detects oversized and stale pools with configurable thresholds
  - swain-design invokes swain-search when spikes enter Active or during ADR research
depends-on: []
addresses: []
---

# Evidence Pool Collection and Normalization

## Goal / Objective

Add a `swain-search` skill that builds reusable evidence pools — collections of normalized source materials (web pages, documents, transcripts, forum threads) that swain-design artifacts can reference. Evidence is cached, shared across artifacts, versioned with the repo, and monitored for staleness and size.

## Scope Boundaries

**In scope:**
- swain-search skill (SKILL.md + references)
- manifest.yaml schema for pool metadata and provenance
- Source normalization to markdown for: web pages, PDFs, video/audio transcripts, forum threads, local documents
- Auto-generated synthesis.md per pool
- evidencewatch script (pool size + freshness monitoring)
- swain-design integration (invoke swain-search on spike Active, ADR research)
- evidence-pool frontmatter field with commit-hash pinning
- Tag-based pool discovery (phase 1)

**Out of scope (phase 2 / future):**
- Semantic pool discovery (matching by content similarity)
- Cross-repo evidence sharing
- Real-time source monitoring / webhooks

## Design Decisions

1. **Auto-generated synthesis** — each pool gets a `synthesis.md` distilled from normalized sources; user-refinable
2. **Generic tool references** — skill references capabilities ("web search", "browser integration"), not specific MCP tool names; graceful degradation when capabilities are unavailable
3. **Git-committed by default** — pools recommended to be in repo (user can gitignore)
4. **Commit-hash pinning** — artifact frontmatter: `evidence-pool: <pool-id>@<commit-hash>`
5. **Storage path** — `docs/evidence-pools/<pool-id>/`

## Pool Structure

```
docs/evidence-pools/<pool-id>/
├── manifest.yaml
├── sources/
│   ├── 001-<slug>.md
│   └── ...
└── synthesis.md
```

## Child Specs

| Spec | Title | Status |
|------|-------|--------|
| SPEC-001 | swain-search skill (SKILL.md, normalization formats, manifest schema) | — |
| SPEC-002 | evidencewatch script (size + freshness monitoring) | — |
| SPEC-003 | swain-design integration (evidence pool hooks, frontmatter linking) | — |

## Key Dependencies

None. This epic extends swain's existing artifact and skill infrastructure.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-09 | — | Initial creation |
