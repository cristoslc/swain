# Changelog

## 2026-04-13 — SPEC-306

### Added
- **X/Twitter thread source type** (`type: x-thread`). URLs matching `(x|twitter|fxtwitter|fixupx).com/.+/status/\d+` route to `scripts/fetch_x_thread.py`, which unrolls the thread via the public fxtwitter API (no auth). Cited posts resolve inline as blockquotes with substantive self-reply continuation (cap 3, link-out for more). Source ID derives as `<handle>-<title-slug>`.
- **Media transcript ingestion** for YouTube, Instagram, and podcast URLs. Tiered fallback chain: VTT subtitles (preferred, `scripts/parse_vtt.py`) → post caption from metadata → scene-change frame extraction + vision OCR → EasyOCR local fallback. Each tier writes `/tmp/swain_search_media_transcript.txt` and normalizes to `sources/<slug>/<slug>.md` with a new `transcript-source` frontmatter field.
- **Bootstrap script** (`scripts/bootstrap.sh`) — idempotent `uv` check with marker file at `~/.local/share/swain-search/.bootstrapped`. Audits settings.json for overly broad permissions on first run. No `gh` requirement.
- **`<SKILL_DIR>` placeholder convention** for script invocations in SKILL.md — resolves to the skill's install path at run time instead of assuming a swain-repo layout.

### Changed
- **`normalization-formats.md`** — added an `x-thread` section with frontmatter and body structure; added `transcript-source: vtt | caption | vision-ocr | local-ocr` to the media section; added `x-thread` to the common frontmatter type enumeration.
- **SKILL.md** — script invocations now use `<SKILL_DIR>/scripts/` instead of `skills/swain-search/scripts/`. This works when the skill is installed under `.claude/skills/swain-search/` in an unrelated project.

### Design notes
- Scripts (`fetch_x_thread.py`, `yt-dlp.sh`, `parse_vtt.py`, `extract_frames.py`, `ocr_frames.py`, `bootstrap.sh`) are modeled after `cristoslc/media-summary`. They are copied in, not submoduled or chained at runtime. Rationale: media-summary ships a gist-publication workflow; swain-search needs the raw transcript as a trove source. Coupled release cadence and install-path friction made submoduling brittle. Sync upstream improvements case by case.
- No gist publication. No public sharing. All output lands in the trove.
