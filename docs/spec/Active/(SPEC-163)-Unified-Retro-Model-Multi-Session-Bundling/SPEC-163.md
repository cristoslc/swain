---
title: "Unified retro model: standalone artifacts with multi-session bundling"
artifact: SPEC-163
track: implementable
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
priority-weight: high
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
  - SPEC-151
  - SPEC-152
  - SPEC-150
  - SPEC-153
depends-on-artifacts:
  - SPEC-151
addresses: []
evidence-pool: "agent-alignment-monitoring@8047381"
source-issue: ""
swain-do: required
---

# Unified retro model: standalone artifacts with multi-session bundling

## Problem Statement

The current retro system has two output modes that overlap: EPIC-scoped retros embed a full `## Retrospective` section in the EPIC artifact, while cross-epic retros produce standalone RETRO docs in `docs/swain-retro/`. This creates two problems:

1. **Duplication.** [SPEC-151](../(SPEC-151)-Retro-Folder-Structure-Manifest-JSONL-Capture/SPEC-151.md) specifies that EPIC-scoped retros "still embed `## Retrospective` in the EPIC AND create a retro folder" — two copies of the same content with no clear source of truth.

2. **Single-session assumption.** [SPEC-151](../(SPEC-151)-Retro-Folder-Structure-Manifest-JSONL-Capture/SPEC-151.md)'s folder structure includes one `session.jsonl.zst` per retro. In practice, an EPIC's work spans many sessions. A retro that only captures the terminal session misses the decision history from earlier sessions where the real work happened.

## Desired Outcomes

Every retro — whether triggered by EPIC completion, manual invocation, or cross-epic reflection — produces exactly one standalone RETRO artifact as its source of truth. EPICs link to the RETRO via `linked-artifacts` and contain a brief `## Retrospective` section with a hyperlink and a one-to-three paragraph summary — enough context for a human reading the EPIC, without duplicating the full retro.

Retro folders support multiple session archives, capturing the full decision history across all sessions that touched the EPIC and its children. Session discovery is artifact-reference-based: the retro skill searches available session logs for mentions of the EPIC ID and its child SPEC/SPIKE/ADR IDs.

## External Behavior

### 1. All retros produce standalone RETRO artifacts

The distinction between "EPIC-scoped embedded" and "standalone" output modes is eliminated. swain-retro always produces a standalone RETRO artifact in `docs/swain-retro/`. The output mode table in SKILL.md becomes:

| Scope | RETRO artifact | EPIC update |
|-------|---------------|-------------|
| **EPIC-scoped** (auto or explicit) | Standalone folder in `docs/swain-retro/` | `linked-artifacts` updated + brief `## Retrospective` section |
| **Cross-epic / time-based** (manual) | Standalone folder in `docs/swain-retro/` | N/A |

### 2. EPIC retrospective section (simplified)

When a retro is produced for an EPIC, the EPIC artifact gets:

- The RETRO artifact ID added to `linked-artifacts` in frontmatter
- A `## Retrospective` section (before `## Lifecycle`) containing:
  - A hyperlinked reference to the RETRO artifact (for humans clicking through)
  - A one-to-three paragraph summary of findings: what was accomplished, key learnings, and notable process observations

```markdown
## Retrospective

See [RETRO-2026-03-23-retro-session-intelligence](../../swain-retro/RETRO-2026-03-23-retro-session-intelligence/RETRO-2026-03-23-retro-session-intelligence.md) for the full retrospective.

This epic shipped all four child specs across N sessions over M days. The
JSONL scrubbing pipeline proved straightforward but session discovery required
iterating on the search strategy — early attempts matched too broadly on common
artifact IDs. The key learning was that bookmark-based session segmentation
produces much better narrative structure than time-based chunking.
```

### 3. Multi-session folder structure

[SPEC-151](../(SPEC-151)-Retro-Folder-Structure-Manifest-JSONL-Capture/SPEC-151.md)'s folder structure is amended. The single `session.jsonl.zst` is replaced by per-session archives flat in the retro folder:

```
docs/swain-retro/
  RETRO-2026-03-23-slug/
    manifest.yaml
    RETRO-2026-03-23-slug.md
    session-summary.md
    session-abc123.jsonl.zst
    session-def456.jsonl.zst
```

Session archives are named `session-<id>.jsonl.zst` (or `.gz`) and sit flat alongside the other retro files. No subdirectory — most retros will have only a few sessions. If no sessions are available (e.g., migrated flat-file retros), no session files exist and `manifest.yaml` records `sessions: []`.

### 4. Manifest schema changes

The manifest's `session` block becomes `sessions` (plural), a list:

```yaml
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
```

Each entry includes `matched-artifacts` — the artifact IDs found in that session log that triggered its inclusion. This provides provenance: why was this session bundled?

### 5. Session discovery

When generating an EPIC-scoped retro, the skill identifies relevant sessions:

1. **Build artifact set.** Collect the EPIC ID and all child artifact IDs (SPECs, SPIKEs, ADRs) using `chart.sh deps <EPIC-ID>`.
2. **Scan session logs.** List JSONL files in `~/.claude/projects/<project-slug>/`. For each file, search for occurrences of any artifact ID in the set.
3. **Rank and filter.** A session is included if it contains at least one reference to an artifact in the set. Record which artifact IDs matched per session.
4. **Capture.** For each matching session, run through the scrub pipeline ([SPEC-150](../(SPEC-150)-Security-Check-JSONL-Scrub-Mode/SPEC-150.md)) and compress as `session-<id>.jsonl.zst` (or `.gz`) in the retro folder.

For manual (non-EPIC) retros, session discovery uses the `linked-artifacts` list from the retro's frontmatter, or falls back to capturing only the current session.

**Scan scope:** All session JSONL files in the project directory are scanned, regardless of age. A SPEC might get attached to an EPIC after the session that worked on it, so filtering by EPIC active dates would miss relevant sessions.

**Performance constraint:** Session log scanning should use simple string matching (grep for artifact IDs), not JSONL parsing. Most projects will have tens of session files, not thousands.

**Compression:** All session archives are compressed (zstd preferred, gzip fallback). No hard size limit per retro — future pruning may be added if retro folders grow too large.

### 6. SPEC-152 interaction

Session summaries ([SPEC-152](../(SPEC-152)-Retro-Session-Summary-Generation/SPEC-152.md)) operate per-session within the bundle. The `session-summary.md` becomes a composite: each session gets its own section within the summary, ordered chronologically by session start time. The four top-level sections (Decision Points, Pivot Points, Surprises, Learnings) synthesize across all sessions.

## Acceptance Criteria

- Given an EPIC transitions to a terminal state, when swain-retro runs, then a standalone RETRO artifact is created in `docs/swain-retro/` (not embedded in the EPIC)
- Given an EPIC-scoped retro is generated, when the EPIC is updated, then the EPIC's `linked-artifacts` includes the RETRO artifact ID and a `## Retrospective` section exists containing a hyperlink to the RETRO and a one-to-three paragraph summary
- Given an EPIC-scoped retro is generated, when session discovery runs, then all session JSONL files referencing the EPIC ID or any child artifact ID are identified
- Given multiple matching sessions exist, when the retro folder is created, then each session has a `session-<id>.jsonl.zst` (or `.gz`) file flat in the retro folder
- Given a matching session exists, when the manifest is written, then the session entry includes `matched-artifacts` listing which artifact IDs were found in that session
- Given no matching sessions are found (e.g., session logs already rotated), when the retro is generated, then `sessions` is an empty list in manifest and the retro document is still generated from git history and artifact state
- Given a single-session retro (manual, non-EPIC), when the retro folder is created, then the current session is captured as `session-<id>.jsonl.zst` flat in the retro folder

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- SPEC-151, SPEC-152, and SPEC-153 have been amended to align with this spec's schema and output model (2026-03-23). This spec governs the unified output model, session discovery, and EPIC update behavior. SPEC-151 owns folder structure and per-session capture mechanics. SPEC-152 owns summary generation format.
- Session discovery is best-effort. Session logs may be rotated, deleted, or unavailable. The retro must still produce useful output from git history and artifact state alone.
- The `## Retrospective` summary in the EPIC is written by the agent at retro time — it is not auto-generated from the RETRO artifact. It should be concise and human-readable, not a mechanical excerpt.
- This spec does not change how swain-retro gathers reflection content (Step 2 in SKILL.md) or extracts memories (Step 3). It only changes the output model (Step 4) and adds session discovery.
- [SPEC-153](../(SPEC-153)-Doctor-Retro-Flat-File-Migration/SPEC-153.md) (flat-file migration) needs a minor update: migrated retros should use `sessions: []` in their manifests since historical JSONL is unavailable.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | Initial creation |
