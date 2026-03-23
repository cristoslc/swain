# Retro Session Intelligence — Design

**Date:** 2026-03-22
**Status:** Draft
**Trove:** agent-alignment-monitoring@8047381

## Context

Swain retros currently capture *what was produced* (artifacts, tasks, commits) but not *how the agent navigated decisions*. The vk4-swain compliance audit (trove source) revealed that session transcripts contain rich process alignment data — decision points, pivots, blind misses, governance bypasses — that retros discard entirely.

Claude Code stores full session transcripts as JSONL files in `~/.claude/projects/<project-slug>/`. These contain every user message, assistant response, tool call, tool result, and progress event. Combined with swain-session bookmarks (which mark key moments during a session), they form a complete decision record.

The goal: retros should archive the session transcript (scrubbed of secrets and PII), generate a structured chronological summary using bookmarks as waypoints, and extract high-level Decision Points, Pivot Points, Surprises, and Learnings — surfacing *process alignment* evidence, not just output quality.

## Design

### Epic structure

| Spec | Title | Type | Depends on |
|------|-------|------|------------|
| SPEC-150 | swain-security-check: JSONL scrub mode | enhancement | — |
| SPEC-151 | swain-retro: folder structure + JSONL capture | enhancement | SPEC-150 |
| SPEC-152 | swain-retro: session summary generation | enhancement | SPEC-151 |
| SPEC-153 | swain-doctor: retro flat-file migration | enhancement | SPEC-151 |

### SPEC-150: JSONL scrub mode

**Problem:** swain-security-check currently scans files and reports findings. For JSONL archival, we need a mode that scans *and redacts* — producing a clean copy rather than a report.

**Approach:**
- New Python script `jsonl_scrub.py` in `swain-security-check/scripts/`
- Reads JSONL from stdin or file path, writes scrubbed JSONL to stdout
- Scrubbing pipeline:
  1. **Strip `file-history-snapshot` entries entirely** — full file backups, high risk, no retro value
  2. **Secret redaction** — reuse gitleaks regex patterns (already configured). Replace matches with `[REDACTED-SECRET]`
  3. **PII redaction** — regex-based: email addresses (`[REDACTED-EMAIL]`), IP addresses (`[REDACTED-IP]`), phone numbers (`[REDACTED-PHONE]`), filesystem paths containing usernames (`/Users/<name>/` → `/Users/[REDACTED-USER]/`)
- Exit codes: 0 = success, 1 = scrub completed with warnings, 2 = error
- Reuses `gitleaks` patterns when gitleaks is installed; falls back to built-in regex patterns for common secret formats (AWS keys, GitHub tokens, etc.) when gitleaks is unavailable

**Key decision:** The scrubber is a *transform*, not a scanner. It always produces output (the scrubbed JSONL), even if no secrets/PII are found. This makes it composable as a pipeline step. The scrubber also emits a JSON scrub report to stderr (entry counts stripped, secrets/PII redacted by category) that SPEC-151's manifest consumes.

**Verification:** Output JSONL must contain zero strings matching the active pattern set (gitleaks or builtin). A test suite provides known-secret and known-PII inputs and asserts redaction in the output.

### SPEC-151: Folder structure, manifest, + JSONL capture

**Problem:** Retros are currently flat files (`docs/swain-retro/YYYY-MM-DD-topic.md`). They need to become folders that can hold the retro doc, session summary, archived JSONL, and a manifest that tracks provenance and scrub metadata. Without a manifest, the folder is just a bag of files with no machine-readable index.

**New structure:**
```
docs/swain-retro/
  RETRO-2026-03-22-vk-build/
    manifest.yaml                    # retro metadata, session provenance, scrub report
    RETRO-2026-03-22-vk-build.md    # retro document
    session-summary.md               # chronological narrative (SPEC-152)
    session.jsonl.zst                # compressed, scrubbed JSONL
```

**Manifest schema (`manifest.yaml`):**
```yaml
retro: RETRO-2026-03-22-vk-build
created: 2026-03-22
scope: "EPIC-042 retro"          # or "cross-epic", "time-based", etc.
period:
  start: 2026-03-22T14:00:00Z
  end: 2026-03-22T18:30:00Z
mode: interactive                 # interactive | auto | manual | scoped

linked-artifacts:
  - EPIC-042
  - SPEC-150
  - SPEC-151

session:
  id: "0af5a96f-933c-48a6-92f6-8bde692033e2"
  project-slug: "-Users-cristos-Documents-code-swain"
  source-path: "~/.claude/projects/-Users-cristos-Documents-code-swain/0af5a96f.jsonl"
  captured: true                  # false if JSONL was missing/rotated
  compression: zst                # zst | gz | none
  archive-file: session.jsonl.zst

scrub:
  scrubber-version: "1.0.0"
  patterns-source: gitleaks       # gitleaks | builtin
  entries-stripped: 16             # file-history-snapshot entries removed
  secrets-redacted: 2
  pii-redacted: 7
  categories:
    - type: secret
      count: 2
      pattern: "AWS access key, GitHub token"
    - type: email
      count: 3
    - type: filesystem-path
      count: 4

summary:
  generated: true                 # false if SPEC-152 not yet implemented
  bookmark-count: 5               # waypoints used for narrative structure
  decision-points: 3
  pivot-points: 2
  surprises: 1
  learnings: 4

memory-files:
  - path: feedback_retro_skill_bypass.md
    type: feedback
    summary: "Agents bypass skills when direct tool use is faster"
```

**JSONL capture flow:**
1. Retro skill identifies the session JSONL file. The project slug is the cwd path with `/` replaced by `-` (e.g., `/Users/cristos/Documents/code/swain` → `-Users-cristos-Documents-code-swain`). The session ID comes from `.agents/session.json` (maintained by swain-session). The JSONL lives at `~/.claude/projects/<project-slug>/<session-id>.jsonl`.
2. If the JSONL file is missing (rotated, deleted, or retro run from a different session): log a warning, set `session.captured: false` in manifest, proceed without JSONL archival. The retro doc is still generated from git/task context.
3. Pipes the JSONL through `jsonl_scrub.py` (SPEC-150), capturing the scrub report for the manifest.
4. Compresses with `zstd` if available (`command -v zstd`); falls back to `gzip`. Sets `session.compression` and `session.archive-file` accordingly (`.jsonl.zst` or `.jsonl.gz`).
5. Archives to the retro folder.

**Changes to swain-retro SKILL.md:**
- All retro output modes (EPIC-scoped and standalone) produce folders instead of flat files
- EPIC-scoped retros still embed the `## Retrospective` section in the EPIC, but *also* create a retro folder for the JSONL archive, manifest, and session summary
- The retro folder is committed to git (the compressed JSONL is typically 50-200KB after scrubbing and compression — acceptable for git)
- Update prior-retro scanning from `ls docs/swain-retro/*.md` to `find docs/swain-retro -name "manifest.yaml"` (machine-readable) or `find docs/swain-retro -name "RETRO-*.md"` (human-readable)
- Manifest is written last (after all other files are in place) so it reflects the final state

### SPEC-152: Session summary generation

**Problem:** Raw JSONL is dense and hard to navigate. Retros need a human-readable chronological summary with high-level process alignment extraction.

**Approach:** Agent-generated at retro time (not scripted heuristics). The retro skill:

1. Reads the scrubbed JSONL (decompressing if needed)
2. Reads swain-session bookmarks from `.agents/session.json` as structural waypoints
3. Generates `session-summary.md` with this structure:

```markdown
# Session Summary

## Decision Points
- [Brief description of each moment where the agent chose between alternatives]

## Pivot Points
- [Moments where the approach changed — failed tool calls, user corrections, strategy shifts]

## Surprises
- [Unexpected outcomes — things that worked against expectations, blockers, scope discoveries]

## Learnings
- [Process insights — what the session reveals about workflow effectiveness]

---

## Chronological Narrative

### [Bookmark: "Started SPEC-042 implementation"] (14:30)

[What happened in this segment — tool calls, decisions made, outcomes]

### [Bookmark: "Pivoted from approach A to B"] (14:45)

[What happened in this segment]

...
```

4. The four top-level sections (Decision Points, Pivot Points, Surprises, Learnings) are LLM-generated from the full session context. They surface *process alignment* evidence — how the agent navigated the work, not just what it produced.

5. The chronological narrative uses bookmarks as section boundaries. Between bookmarks, it summarizes the key actions (tool calls, user interactions, outcomes) without reproducing the full transcript.

**Bookmark fallback:** If `.agents/session.json` has no bookmarks or swain-session isn't installed, the summary falls back to time-based chunking — every ~15 minutes of session activity becomes a narrative section. Bookmarks improve structure but are not required.

**Token management:** Session JSONL files can be large (500KB-2.5MB). The summary generation reads the scrubbed JSONL, which is already smaller (no file-history-snapshots). If the scrubbed JSONL exceeds ~200K tokens after stripping, the skill processes it in chronological chunks (bounded by bookmarks or 15-minute windows), generating per-chunk summaries that are then synthesized into the final session-summary.md.

**Verification note:** SPEC-152's output is LLM-generated and non-deterministic. Acceptance criteria verify structural completeness (all four sections present, chronological ordering, bookmark references) but not content quality. Content quality is verified by operator review — this is an inherent property of interpretive summarization.

### SPEC-153: swain-doctor retro flat-file migration

**Problem:** Existing retros are flat files in `docs/swain-retro/`. After SPEC-151, the convention is folders. swain-doctor should detect and migrate.

**Approach:**
- Detection: scan `docs/swain-retro/` for `.md` files that are not inside a subdirectory
- Migration: for each flat file `YYYY-MM-DD-topic.md`:
  1. Create folder `RETRO-YYYY-MM-DD-topic/`
  2. Move file to `RETRO-YYYY-MM-DD-topic/RETRO-YYYY-MM-DD-topic.md`
  3. `git mv` for clean history
- No JSONL or session summary is retroactively generated (those sessions are gone)
- Idempotent — safe to run multiple times

## Decisions

1. **Scrubber as transform, not scanner** — always produces output, composable in pipelines
2. **Agent-generated extraction over script heuristics** — Decision Points / Pivot Points / Surprises / Learnings require interpretive reasoning that heuristics can't capture
3. **Bookmarks as waypoints** — leverages existing swain-session infrastructure for narrative structure
4. **JSONL committed to git** — compressed size (50-200KB) is acceptable; keeps the archive co-located with the retro for discoverability
5. **Folder structure uses RETRO-ID convention** — consistent with other artifact types
6. **swain-security-check extended, not duplicated** — keeps security scrubbing centralized
7. **zstd compression with gzip fallback** — zstd offers better ratios for JSONL; gzip as universal fallback. Detection via `command -v zstd`. File extension changes accordingly (`.jsonl.zst` vs `.jsonl.gz`)
8. **Retro manifest** — machine-readable YAML index per retro folder, tracking session provenance, scrub metadata, summary stats, and memory file references. Enables programmatic retro discovery and cross-retro analysis
9. **SPEC-152 is non-deterministic by design** — acceptance criteria verify structure, not content. Operator review is the quality gate
10. **Bookmark fallback to time-based chunking** — swain-session bookmarks are preferred but not required; 15-minute windows provide adequate structure without them
