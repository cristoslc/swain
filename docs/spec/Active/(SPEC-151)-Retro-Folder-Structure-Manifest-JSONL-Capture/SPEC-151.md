---
title: "swain-retro: folder structure, manifest, + JSONL capture"
artifact: SPEC-151
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
  - SPEC-152
  - SPEC-153
  - SPEC-163
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
    manifest.yaml                         # retro metadata, session provenance, scrub report
    RETRO-2026-03-22-vk-build.md         # retro document
    session-summary.md                    # placeholder until SPEC-152 (empty file with header)
    session-<id-1>.jsonl.zst             # compressed, scrubbed JSONL per session
    session-<id-2>.jsonl.zst             # (zero or more — flat in folder)
```

Session archives live flat in the retro folder (no subdirectory). A retro may contain zero, one, or many session archives depending on how many sessions touched the relevant artifacts. See SPEC-163 for session discovery logic.

**Manifest schema:**

```yaml
retro: RETRO-2026-03-22-vk-build
created: 2026-03-22
scope: "EPIC-042 retro"
period:
  start: 2026-03-22T14:00:00Z
  end: 2026-03-22T18:30:00Z
mode: interactive

linked-artifacts:
  - EPIC-042
  - SPEC-150
  - SPEC-151

sessions:
  - id: "abc123"
    source-path: "~/.claude/projects/-Users-cristos-Documents-code-swain/abc123.jsonl"
    captured: true
    compression: zst
    archive-file: session-abc123.jsonl.zst
    matched-artifacts:
      - SPEC-151
      - SPEC-152
  - id: "def456"
    source-path: "~/.claude/projects/-Users-cristos-Documents-code-swain/def456.jsonl"
    captured: true
    compression: zst
    archive-file: session-def456.jsonl.zst
    matched-artifacts:
      - EPIC-042
      - SPEC-150

scrub:
  scrubber-version: "1.0.0"
  patterns-source: gitleaks
  entries-stripped: 16
  secrets-redacted: 2
  pii-redacted: 7

summary:
  generated: false
  bookmark-count: 0

memory-files: []
```

Each session entry includes `matched-artifacts` — the artifact IDs found in that session log that triggered its inclusion (provenance). When no sessions are available, `sessions: []`.

**JSONL capture flow (per session):**
1. Identify session JSONL files. Session discovery (SPEC-163) provides the list of session IDs and paths to capture.
2. For each session: if JSONL missing, record `captured: false` in manifest entry, log warning, skip
3. Pipe through `jsonl_scrub.py` (SPEC-150), capture scrub report JSON from stderr
4. Compress: `zstd` if available (`command -v zstd`), else `gzip`. Name as `session-<id>.jsonl.zst` (or `.gz`)
5. Write manifest last (reflects final state of all other files)

**SKILL.md changes:**
- All output modes produce folders
- EPIC update behavior is governed by SPEC-163 (standalone RETRO artifact + link/summary in EPIC — not full embedded duplication)
- Prior-retro scanning updated from `ls docs/swain-retro/*.md` to `find docs/swain-retro -name "manifest.yaml"`

**Preconditions:** SPEC-150 (jsonl_scrub.py) is implemented. zstd or gzip available.
**Postconditions:** Retro folder exists with manifest.yaml, retro doc, and compressed scrubbed archives for each discovered session (if available).

## Acceptance Criteria

- Given a retro is generated (any mode), when the retro completes, then a folder `docs/swain-retro/RETRO-<date>-<slug>/` exists containing at minimum `manifest.yaml` and `RETRO-<date>-<slug>.md`
- Given session discovery (SPEC-163) identifies N sessions, when JSONL capture runs, then each captured session produces a `session-<id>.jsonl.zst` (or `.gz`) file flat in the retro folder
- Given a session's JSONL file is missing, when capture runs for that session, then the manifest entry has `captured: false` and no archive file is created for it
- Given no sessions are discovered, when the retro is generated, then `sessions: []` in manifest and the retro doc is still generated from git history and artifact state
- Given a manifest.yaml is generated, then it contains valid YAML with all required top-level keys: `retro`, `created`, `scope`, `period`, `mode`, `linked-artifacts`, `sessions`, `scrub`
- Given zstd is not installed, when JSONL is archived, then gzip is used and each session entry has `compression: gz` and `archive-file: session-<id>.jsonl.gz`

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Manifest is written by the retro skill (not a separate script) — it's part of the retro generation flow
- The `session-summary.md` file is a placeholder in this spec (just a header + "Summary pending SPEC-152"). SPEC-152 populates it with content.
- No hard limit on total compressed JSONL size. Compression (zstd preferred) is always applied. Future pruning may be added if retro folders grow too large.
- SPEC-163 governs session discovery, the unified output model, and EPIC update behavior. This spec owns the folder structure, manifest schema, and per-session capture mechanics.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
