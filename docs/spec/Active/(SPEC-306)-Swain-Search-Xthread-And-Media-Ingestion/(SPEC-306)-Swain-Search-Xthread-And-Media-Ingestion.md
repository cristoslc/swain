---
title: "swain-search: X-Thread Source Type and Media Transcript Ingestion"
artifact: SPEC-306
track: implementable
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-search: X-Thread Source Type and Media Transcript Ingestion

## Problem Statement

swain-search treats X threads and media URLs as generic sources. Threads fall into the forum path. That path loses thread structure, cited posts, and self-reply chains. Media URLs get vague "use a transcription capability" guidance. There is no concrete flow for captions, fallback text, or frame OCR. Both paths produce low-fidelity trove sources.

The `media-summary` skill has tested scripts that produce what swain-search wants. `fetch_x_thread.py` unrolls threads via `api.fxtwitter.com`. It resolves cited posts and self-replies. `yt-dlp.sh` pulls subtitles and metadata. `parse_vtt.py` makes clean timestamped transcripts. `extract_frames.py` and `ocr_frames.py` handle vision OCR as a fallback.

Those scripts target summary publication, not trove ingestion. Reusing them by submoduling fails three ways. The swain install pipeline does not carry submodules. The primary output is a published gist, not a trove source. Coupled release cadence would force swain-search to track upstream breaks.

## Desired Outcomes

A researcher pastes an X thread URL or a YouTube URL into swain-search. They get a first-class trove source. X threads come back as verbatim posts with cited posts resolved. Media URLs come back as a timestamped transcript with speaker labels. Both land in the trove next to other sources.

The researcher does not need `media-summary` installed. Nothing gets published. No template rendering is needed. Later artifacts can cite the thread or transcript by trove hash and reproduce it exactly.

## External Behavior

### Inputs

- URLs passed as sources during Create or Extend mode.
- URL classification happens in the source-collection loop of SKILL.md.

### Classification

| Signal | Source type |
|--------|-------------|
| URL matches `(x\|twitter\|fxtwitter\|fixupx)\.com/.+/status/\d+` | `x-thread` |
| URL matches `youtube.com`, `youtu.be`, `instagram.com`, or resolves to a YouTube equivalent | `media` |

All other URLs continue to use the existing `web` / `forum` paths — no change.

### X-thread path

1. Fetch via `scripts/fetch_x_thread.py <URL>` (stdlib-only; calls `api.fxtwitter.com/2/thread/{id}`; no auth).
2. If the response indicates a single-post response on a known thread-opener (account-proxy missing), mark the source `failed: true` with reason `x-thread-unrollable` and continue. Do not halt the trove.
3. Normalize to markdown per the new `x-thread` entry in `references/normalization-formats.md`: frontmatter with author metadata, body as numbered verbatim posts with per-post hyperlinks, cited-post blockquotes with self-reply continuation, inline `@mention` and `#hashtag` hyperlinking.
4. Write to `sources/<source-id>/<source-id>.md` where `<source-id>` is `<handle>-<first-few-words>` (sanitized per existing slug rules).

### Media path

1. Run `scripts/bootstrap.sh` once per session (idempotent, marker-gated at `~/.local/share/swain-search/.bootstrapped`); verify `uv` is on PATH.
2. Run `scripts/yt-dlp.sh --write-auto-sub --sub-lang en --write-info-json --skip-download --sub-format vtt -o "/tmp/swain_media_transcript" "<URL>"`.
3. If `/tmp/swain_media_transcript.en.vtt` exists and is non-empty: run `scripts/parse_vtt.py` to produce timestamped segments. This is the success path.
4. If no VTT: read `/tmp/swain_media_transcript.info.json` `description`; if >100 non-hashtag chars, use that as the transcript.
5. If caption insufficient: ask the operator to approve frame extraction. On approval, download the video and run `scripts/extract_frames.py` + vision-OCR (Read tool on each frame); fall back to `scripts/ocr_frames.py` (EasyOCR) if vision probing fails.
6. Normalize to markdown per the existing `media` entry in `references/normalization-formats.md` (no changes to that schema). Transcript lines carry `[HH:MM:SS]` prefixes when available; omit timestamps for caption or OCR-sourced transcripts.
7. Write to `sources/<source-id>/<source-id>.md` where `<source-id>` is the video title slug.

### Script location and invocation

All new scripts live under `skills/swain-search/scripts/`. SKILL.md invokes them via the `<SKILL_DIR>` placeholder (e.g., `bash "<SKILL_DIR>/scripts/bootstrap.sh"`). This matches the `media-summary` pattern. It replaces the hardcoded `skills/swain-search/scripts/...` paths in SKILL.md today. Those paths assume the skill sits inside the swain repo. They break when the skill is installed under `.claude/skills/` in another project.

### Constraints

- No gist publication. swain-search output is a trove source, not a shared summary. No `gh gist create` anywhere.
- No summary generation. The media path produces a raw transcript. Cross-source synthesis happens in `synthesis.md`, as today.
- No runtime chain into `/media-summary`. swain-search owns the transcript path. Trove fidelity does not depend on another skill.
- No changes to trove manifest schema. x-thread and media sources use existing fields. Any per-type metadata goes in the source frontmatter.
- Paywall proxy, snapshot gate, prior-art check, and dual-commit stamping stay as they are. x-thread and media sources inherit the existing trove lifecycle.

## Acceptance Criteria

**AC1 — X-thread ingestion**
Given an X/Twitter status URL passed as a source in Create or Extend mode,
When swain-search processes it,
Then a file at `sources/<handle>-<slug>/<handle>-<slug>.md` exists with frontmatter fields `source-id`, `title`, `type: x-thread`, `url`, `fetched`, `hash`, `author-handle`, `author-name`, `published-date`, `tweet-count`; and the body renders every post verbatim as a numbered list with per-post hyperlinks.

**AC2 — Cited posts and self-replies**
Given an X thread that references other X statuses,
When swain-search normalizes it,
Then each referenced status appears as an indented blockquote directly below the citing post, with substantive self-replies appended as continuation (cap 3, link-out for more), and bare-URL self-replies skipped.

**AC3 — YouTube transcript ingestion**
Given a YouTube URL with available auto-generated captions,
When swain-search processes it,
Then a file at `sources/<slug>/<slug>.md` exists with frontmatter `type: media`, and the body contains a timestamped transcript (one segment per line, `[HH:MM:SS]` prefix) derived from the VTT file.

**AC4 — Caption fallback**
Given a media URL without VTT captions but with a post description >100 non-hashtag characters,
When swain-search processes it,
Then the normalized source contains the caption text as the transcript body without timestamps, and frontmatter flags `transcript-source: caption`.

**AC5 — Frame-extraction fallback with operator approval**
Given a media URL with neither captions nor sufficient description,
When swain-search asks the operator to approve vision-OCR frame extraction and the operator approves,
Then the normalized source contains extracted text deduplicated across frames, and frontmatter flags `transcript-source: vision-ocr` (or `local-ocr` when EasyOCR is used).

**AC6 — Unrollable thread fails gracefully**
Given an X thread where fxtwitter returns a single-post response but the opener indicates a longer thread,
When swain-search processes it,
Then the manifest entry records `failed: true` with `reason: x-thread-unrollable`, no source file is written, and the trove run continues with remaining sources.

**AC7 — Bootstrap idempotency**
Given a fresh environment,
When the media path runs for the first time,
Then `scripts/bootstrap.sh` verifies `uv` is available, creates `~/.local/share/swain-search/.bootstrapped`, and subsequent invocations exit in under 100ms without re-checking.

**AC8 — SKILL_DIR convention**
Given SKILL.md after this change,
When any script is invoked,
Then the invocation uses the `<SKILL_DIR>/scripts/<name>` placeholder form, and no bash line hardcodes `skills/swain-search/` as a path prefix for scripts introduced by this spec.

**AC9 — Trove lifecycle unchanged**
Given an x-thread or media source is added to a trove,
When Create or Extend mode completes,
Then the dual-commit stamping, paywall proxy gate, snapshot evidence gate (where applicable), prior-art check, and synthesis regeneration all execute per the existing workflow without modification.

## Verification

<!-- Populated on transition to NeedsManualTest. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope**:
- New scripts in `skills/swain-search/scripts/`: `fetch_x_thread.py`, `yt-dlp.sh`, `parse_vtt.py`, `extract_frames.py`, `ocr_frames.py`, `bootstrap.sh`. Copied from `cristoslc/media-summary` and shaped for trove output. No gist, no templates.
- SKILL.md updates: x-thread detection, media flow with tiered fallback, and `<SKILL_DIR>` migration for script paths.
- `references/normalization-formats.md` additions: a new `x-thread` section with frontmatter and body rules. The media section gains a `transcript-source` field. No other changes.
- New CHANGELOG.md and README.md for the skill. Pattern matches `media-summary`: scoped allowed-tool entries and security notes.

**Out of scope** (reject if scope creep pressures these in):
- Submoduling or runtime chaining into `media-summary`.
- Gist publication or any `gh gist` call.
- Per-source summary generation. Summaries live in `synthesis.md`, as today.
- Recipe-video templates or recipe classification.
- Content-type classification (`general` vs `recipe`).
- Retroactive migration of existing troves to the new source types.
- Vendoring `media-summary` as an npm dep of swain.

**Non-goals**:
- No changes to trove manifest schema.
- No changes to the trove commit stamping pattern.
- No changes to the paywall proxy registry.
- No claim to upstream maintenance of `fetch_x_thread.py`. Future fixes in `media-summary` sync case by case.

**Token-budget**: script copies are small. `fetch_x_thread.py` is about 400 lines. The others are under 100 each. SKILL.md additions are bounded to the new detection rows and the two new flow sections. The file stays readable in one pass.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | 2bf515cb | Initial creation; user-approved scope (b-option: infrastructure patterns + X-thread + media paths; no submodule, no runtime chain). |
