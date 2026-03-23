---
title: "swain-retro: folder structure, manifest, + JSONL capture"
artifact: SPEC-151
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
depends-on-artifacts:
  - SPEC-150
addresses: []
evidence-pool: "agent-alignment-monitoring@8047381"
source-issue: ""
swain-do: required
---

# swain-retro: folder structure, manifest, + JSONL capture

## Problem Statement

Retros are currently flat markdown files in `docs/swain-retro/`. This structure cannot accommodate session archives (scrubbed JSONL), session summaries, or machine-readable metadata. Without a manifest, retros are opaque to programmatic discovery and cross-retro analysis.

## Desired Outcomes

Every retro becomes a self-contained folder with a machine-readable manifest. Operators and agents can discover retros programmatically (via manifests), understand what session data was captured, and access the scrubbed JSONL for forensic or self-study use. The manifest makes cross-retro pattern detection possible in future work.

## External Behavior

**New folder structure:**
```
docs/swain-retro/
  RETRO-2026-03-22-vk-build/
    manifest.yaml                    # retro metadata, session provenance, scrub report
    RETRO-2026-03-22-vk-build.md    # retro document
    session-summary.md               # placeholder until SPEC-152 (empty file with header)
    session.jsonl.zst                # compressed, scrubbed JSONL (or .jsonl.gz)
```

**Manifest schema:** See design doc `2026-03-22-retro-session-intelligence-design.md` for full schema. Key sections: retro metadata, linked-artifacts, session provenance, scrub report, summary stats, memory-files.

**JSONL capture flow:**
1. Identify session JSONL: project slug = cwd with `/` → `-`; session ID from `.agents/session.json`; file at `~/.claude/projects/<slug>/<session-id>.jsonl`
2. If JSONL missing: set `session.captured: false` in manifest, log warning, proceed without archive
3. Pipe through `jsonl_scrub.py` (SPEC-150), capture scrub report JSON from stderr
4. Compress: `zstd` if available (`command -v zstd`), else `gzip`. Set `session.compression` and `session.archive-file` accordingly
5. Write manifest last (reflects final state of all other files)

**SKILL.md changes:**
- All output modes (EPIC-scoped, standalone) produce folders
- EPIC-scoped retros still embed `## Retrospective` in the EPIC AND create a retro folder
- Prior-retro scanning updated from `ls docs/swain-retro/*.md` to `find docs/swain-retro -name "manifest.yaml"`

**Preconditions:** SPEC-150 (jsonl_scrub.py) is implemented. zstd or gzip available.
**Postconditions:** Retro folder exists with manifest.yaml, retro doc, and (if session JSONL was available) compressed scrubbed archive.

## Acceptance Criteria

- Given a retro is generated (any mode), when the retro completes, then a folder `docs/swain-retro/RETRO-<date>-<slug>/` exists containing at minimum `manifest.yaml` and `RETRO-<date>-<slug>.md`
- Given the current session's JSONL file exists, when a retro is generated, then `session.jsonl.zst` (or `.gz`) is present in the folder and `session.captured: true` in manifest
- Given the current session's JSONL file is missing, when a retro is generated, then `session.captured: false` in manifest and no archive file exists, but the retro doc is still generated
- Given a manifest.yaml is generated, then it contains valid YAML with all required top-level keys: `retro`, `created`, `scope`, `period`, `mode`, `linked-artifacts`, `session`, `scrub`
- Given an EPIC-scoped retro, when generated, then both the EPIC's `## Retrospective` section AND the retro folder are created
- Given zstd is not installed, when JSONL is archived, then gzip is used and `session.compression: gz` and `session.archive-file: session.jsonl.gz` in manifest

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Manifest is written by the retro skill (not a separate script) — it's part of the retro generation flow
- The `session-summary.md` file is a placeholder in this spec (just a header + "Summary pending SPEC-152"). SPEC-152 populates it with content.
- Compressed JSONL size should be logged; if >500KB, warn the operator before committing

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
