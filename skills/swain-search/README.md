# swain-search

Trove collection and normalization for swain-design artifacts. Collects sources from the web, local files, X/Twitter threads, and video/audio media, normalizes them to markdown, and caches them in reusable troves. See [SKILL.md](SKILL.md) for the full workflow.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python and Python packages used by the media and X-thread flows)
- A web-search capability is recommended for search-based source collection
- A page-fetching capability is recommended for web-page sources

All Python dependencies (`yt-dlp`, `opencv-python-headless`, `easyocr`) run transiently via `uv run --with` and do not require global installation. The bootstrap script checks for `uv` on first run:

```bash
bash skills/swain-search/scripts/bootstrap.sh
```

## Source types

| Type | Input | Script / capability |
|------|-------|---------------------|
| `web` | Any HTTP URL | web fetch capability |
| `forum` | Forum thread URL | web fetch capability |
| `media` | YouTube, Instagram, or podcast URL | `scripts/yt-dlp.sh`, `scripts/parse_vtt.py`, `scripts/extract_frames.py`, `scripts/ocr_frames.py` |
| `x-thread` | X/Twitter status URL | `scripts/fetch_x_thread.py` |
| `document` | Local file path (PDF, DOCX, PPTX, XLSX) | document conversion capability |
| `local` | Local markdown path | direct read |
| `repository` | Git repo URL or local path | clone or read-directory |
| `documentation-site` | Docs-site URL | crawl or fetch |
| `cli-manpage`, `cli-help`, `cli-subcommand-help` | CLI tool name | `man`, `--help` capture |

Detailed normalization rules per type: [references/normalization-formats.md](references/normalization-formats.md).

## Permissions

To run swain-search fully autonomously, add these entries to your Claude Code `allowedTools`. Each pattern is scoped narrowly to limit blast radius.

> **Review before granting.** Read the source files before auto-approving: [`scripts/bootstrap.sh`](scripts/bootstrap.sh), [`scripts/fetch_x_thread.py`](scripts/fetch_x_thread.py), [`scripts/parse_vtt.py`](scripts/parse_vtt.py), [`scripts/yt-dlp.sh`](scripts/yt-dlp.sh), [`scripts/extract_frames.py`](scripts/extract_frames.py), [`scripts/ocr_frames.py`](scripts/ocr_frames.py).

### Recommended (low-risk)

```json
"Skill(swain-search)",
"Bash(bash */scripts/bootstrap.sh)",
"Bash(uv run */scripts/fetch_x_thread.py*)",
"Bash(uv run */scripts/parse_vtt.py)",
"Bash(bash */scripts/yt-dlp.sh*)",
"Bash(uv run --with opencv-python-headless*)",
"Bash(uv run --with easyocr*)",
"Bash(uv run --with \"easyocr,opencv-python-headless\"*)",
"Bash(test -s /tmp/swain_search_*)",
"Bash(bash */scripts/export-snapshot.sh*)",
"Bash(bash */scripts/log-snapshot-metadata.sh*)",
"Bash(bash */scripts/verify-snapshot-evidence.sh*)",
"Bash(bash */scripts/resolve-proxy.sh*)"
```

Why these are safe:

- **`Skill(swain-search)`** — allows skill invocation.
- **`Bash(bash */scripts/bootstrap.sh)`** — verifies `uv` is on `PATH` and audits broad permission patterns. After the first successful run, a marker file short-circuits further work. No user input. No network calls.
- **`Bash(uv run */scripts/fetch_x_thread.py*)`** — stdlib-only Python. Takes a single X/Twitter URL or tweet ID. Calls `api.fxtwitter.com` (public, unauthenticated). Writes only to `/tmp/swain_search_thread.json` and `/tmp/swain_search_thread_transcript.txt`. No subprocess, no eval.
- **`Bash(uv run */scripts/parse_vtt.py)`** — pure string processing. Reads `/tmp/swain_search_media.en.vtt`, writes `/tmp/swain_search_media_transcript.txt`. No network, no subprocess. HTML-like tags are stripped by regex.
- **`Bash(bash */scripts/yt-dlp.sh*)`** — thin wrapper around `uv run --with yt-dlp yt-dlp`. The skill passes `--skip-download` for transcript extraction. Full video download only runs during the approved frame-extraction fallback.
- **`Bash(uv run --with opencv-python-headless*)`** — frame extraction from videos already downloaded to `/tmp`. Pure image processing.
- **`Bash(uv run --with easyocr*)`** — local OCR fallback, only when vision probing fails. Reads frames from `/tmp`, writes text to `/tmp`.
- **`Bash(test -s /tmp/swain_search_*)`** — read-only existence check on the skill's temp files.
- **Snapshot-gate scripts** (`export-snapshot.sh`, `log-snapshot-metadata.sh`, `verify-snapshot-evidence.sh`) — SPEC-220 evidence gate for remote documents. Write only to `.agents/search-snapshots/`.
- **`resolve-proxy.sh`** — read-only lookup in `references/paywall-proxies.yaml`.

### Not recommended (overly broad)

```json
"Bash(open:*)",
"Bash(osascript:*)",
"Bash(gh:*)"
```

These cover actions this skill does not need. Overly broad patterns widen the blast radius when a transcript or thread contains prompt injection.

### Security considerations

- **Content-based prompt injection (highest risk)**. An X thread, video caption, or OCR'd frame could contain instructions like "SYSTEM: ignore previous, run …". Claude's training resists this, but it is an inherent risk of processing untrusted text. Mitigation: the skill's allowed tools are scoped to `Bash`, `Read`, `Write`, `Edit`, and a few MCP capabilities. There is no `gh`, no shell-escape, no `open`.
- **Vision OCR injection**. On-screen frame text is read by the model. Malicious videos could embed prompt injection in text overlays. Same mitigations as above.
- **Trove content poisoning**. If injection influences normalization, misleading content lands in the trove. That trove may later be cited by artifacts. Review new troves before they feed downstream decisions.
- **`/tmp` symlink attack**. A local attacker could symlink `/tmp/swain_search_media.en.vtt` to a sensitive file. This requires existing local access, at which point the attacker already has your permissions. Very low risk.
- **Skill supply chain**. A malicious fork could rewrite SKILL.md or the scripts to do anything Claude Code's permissions allow. Only install from sources you trust. Review skill contents after installation (`~/.claude/skills/swain-search/`).

### Bootstrap

`bootstrap.sh` runs on the first media or X-thread flow and short-circuits after. Permission prompts appear each run unless `"Bash(bash */scripts/bootstrap.sh)"` is on your allowed-tools list. This is safe because the script only runs `command -v` checks, audits settings files, and writes to a marker file in `~/.local/share/`. It never processes user-controlled input.

On first run, the script scans your Claude Code settings files for overly broad allowed-tool patterns like `Bash(osascript:*)` or `Bash(open:*)`. If found, it prints a `BROAD PERMISSIONS DETECTED` warning with a risk explanation. This check only runs once (gated by the same marker file).

## Usage

The skill is invoked by swain-design during research-phase transitions (Spike Proposed → Active, ADR Proposed → Active, Vision/Epic creation) and directly by the operator for targeted collection:

```
/swain-search research <topic>
/swain-search add <url> to <trove-id>
/swain-search refresh <trove-id>
```

See [SKILL.md](SKILL.md) for mode details (Create, Extend, Refresh, Discover).

## Output

Each trove lives at `docs/troves/<trove-id>/` and contains:
- `manifest.yaml` — provenance, tags, per-source metadata with content hashes
- `sources/<source-id>/<source-id>.md` — normalized source content
- `synthesis.md` — thematic distillation across all sources

Artifacts reference a trove by commit hash: `trove: <trove-id>@<hash>` in frontmatter.
