---
name: swain-search
description: "Trove collection and normalization for swain-design artifacts. Collects sources from the web, local files, and media (video/audio), normalizes them to markdown, and caches them in reusable troves. Use when researching a topic for a spike, ADR, vision, or any artifact that needs structured research. Also use to refresh stale troves or extend existing ones with new sources. Triggers on: 'research X', 'gather sources for', 'build a trove', 'search for sources about', 'refresh the trove', 'what do we know about X', or when swain-design needs research inputs for a spike or ADR."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, WebSearch, WebFetch
metadata:
  short-description: Trove collection and normalization
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: opus, effort: high -->

# swain-search

Collect, normalize, and cache source materials into reusable troves that swain-design artifacts can reference.

## Mode detection

| Signal | Mode |
|--------|------|
| No trove exists for the topic, or user says "research X" / "gather sources" | **Create** — new trove |
| Trove exists and user provides new sources or says "add to" / "extend" | **Extend** — add sources to existing trove |
| Trove exists and user says "refresh" or sources are past TTL | **Refresh** — re-fetch stale sources |
| User asks "what troves do we have" or "find sources about X" | **Discover** — search existing troves by tag |

## Create mode

Build a new trove from scratch.

### Step 1 — Gather inputs

Ask the user (or infer from context) for:

1. **Trove ID** — a slug for the topic (e.g., `websocket-vs-sse`). Suggest one if the context is clear.
2. **Tags** — keywords for discovery (e.g., `real-time`, `websocket`, `sse`)
3. **Sources** — any combination of:
   - Web search queries ("search for WebSocket vs SSE comparisons")
   - URLs (web pages, forum threads, docs)
   - Video/audio URLs
   - Local file paths
4. **Freshness TTL overrides** — optional, defaults are fine for most troves

If invoked from swain-design (e.g., spike entering Active), the artifact context provides the topic, tags, and sometimes initial sources.

### Step 2 — Collect and normalize

For each source, use the appropriate capability. Read `skills/swain-search/references/normalization-formats.md` for the exact markdown structure per source type.

**Web search queries:**
1. Use a web search capability to find relevant results
2. Select the top 3-5 most relevant results
3. For each: fetch the page, normalize to markdown per the web page format
4. If no web search capability is available, tell the user and skip

**Web page URLs:**
1. Fetch the page using a browser or page-fetching capability
2. Strip boilerplate (nav, ads, sidebars, cookie banners)
3. Normalize to markdown per the web page format
4. If fetch fails, record the URL in manifest with a `failed: true` flag and move on

**Video/audio URLs:**
1. Use a media transcription capability to get the transcript
2. Normalize to markdown per the media format (timestamps, speaker labels, key points)
3. If no transcription capability is available, tell the user and skip — or accept a pre-made transcript

**Local files:**
1. Use a document conversion capability (PDF, DOCX, etc.) or read directly if already markdown
2. Normalize per the document format
3. For markdown files: add frontmatter only, preserve content

**Forum threads / discussions:**
1. Fetch and normalize per the forum format (chronological, author-attributed)
2. Flatten nested threads to chronological order with reply-to context

**Repositories:**
1. Clone or read the repository contents
2. Mirror the original directory tree under `sources/<source-id>/`
3. Default: mirror the full tree. For large repositories (thousands of files), ingest selectively and set `selective: true` in the manifest entry
4. Populate the `highlights` array with paths to the most important files (relative to the source-id directory)

**Documentation sites:**
1. Crawl or fetch the documentation site
2. Mirror the section hierarchy under `sources/<source-id>/`
3. Default: mirror the full site. For large sites, ingest selectively and set `selective: true`
4. Populate the `highlights` array with paths to the most important pages
5. Preserve internal link structure where possible

Each normalized source gets a **slug-based source ID** and lives in a directory-per-source layout:
- **Flat sources** (web, forum, media, document, local): `sources/<source-id>/<source-id>.md`
- **Hierarchical sources** (repository, documentation-site): `sources/<source-id>/` with the original tree mirrored inside

**Source ID generation:**
- Derive the source ID as a slug from the source title or URL (e.g., `mdn-websocket-api`, `strangeloop-2025-realtime`)
- When a slug collides with an existing source ID: append `__word1-word2` using two random words from `skills/swain-search/references/wordlist.txt`
- If the wordlist is missing, append `__` followed by 4 hex characters (e.g., `__a3f8`) as a fallback

### Step 3 — Generate manifest

Create `manifest.yaml` following the schema in `skills/swain-search/references/manifest-schema.md`. Include:
- Trove metadata (id, created date, tags)
- Default freshness TTL per source type
- One entry per source with provenance (URL/path, fetch date, content hash, type)

Compute content hashes as bare hex SHA-256 digests (no prefix) of the normalized markdown content:

```bash
shasum -a 256 sources/mdn-websocket-api/mdn-websocket-api.md | cut -d' ' -f1
```

### Step 4 — Generate synthesis

Create `synthesis.md` — a structured distillation of key findings across all sources.

Structure the synthesis by **theme**, not by source. Group related findings together, cite sources by ID, and surface:
- **Key findings** — what the sources collectively say about the topic
- **Points of agreement** — where sources converge
- **Points of disagreement** — where sources conflict or present alternatives
- **Gaps** — what the sources don't cover that might matter

Keep it concise. The synthesis is a starting point, not a comprehensive report — the user or artifact author will refine it.

### Step 5 — Commit and stamp

Use the dual-commit pattern (same as swain-design lifecycle stamps) to give the trove a reachable commit hash.

**Before Commit A** — append a `history` entry to `manifest.yaml` with a `--` placeholder for the commit hash:

```yaml
history:
  - event: created
    date: 2026-03-09
    commit: "--"
    sources: 3
```

**Commit A** — commit the trove content:

```bash
git add docs/troves/<trove-id>/
git commit -m "research(<trove-id>): create trove with N sources"
TROVE_HASH=$(git rev-parse HEAD)
```

**Commit B** — back-fill the commit hash into the history entry, then update the referencing artifact's frontmatter (if one exists):

```bash
# Replace "--" with the real hash in the history entry
# Update artifact frontmatter: trove: <trove-id>@<TROVE_HASH>
git add docs/troves/<trove-id>/manifest.yaml
git add docs/<artifact-type>/<phase>/<artifact-dir>/   # if artifact exists
git commit -m "docs(<trove-id>): stamp history hash ${TROVE_HASH:0:7}"
```

If no referencing artifact exists yet (standalone research), Commit B still stamps the history entry — report the hash so it can be referenced later.

### Step 6 — Report

Tell the user what was created:

> **Trove `<trove-id>` created** with N sources — committed as `<TROVE_HASH:0:7>`.
>
> - `docs/troves/<trove-id>/manifest.yaml` — provenance and metadata
> - `docs/troves/<trove-id>/sources/` — N normalized source files
> - `docs/troves/<trove-id>/synthesis.md` — thematic distillation
>
> Reference from artifacts with: `trove: <trove-id>@<TROVE_HASH:0:7>`

## Extend mode

Add new sources to an existing trove.

1. Read the existing `manifest.yaml`
2. Collect and normalize new sources (same as Create step 2)
3. Assign slug-based source IDs to new sources (following the same ID generation rules)
4. Append new entries to `manifest.yaml`
5. Update `refreshed` date
6. Regenerate `synthesis.md` incorporating all sources (old + new)
7. Append a `history` entry with `event: extended` and `commit: "--"` placeholder
8. Commit and stamp (same dual-commit pattern as Create step 5):
   - **Commit A**: `git commit -m "research(<trove-id>): extend with N new sources"`
   - Capture `TROVE_HASH=$(git rev-parse HEAD)`
   - **Commit B**: back-fill hash in history entry, update referencing artifact frontmatter (if artifact exists)
9. Report what was added, including the new commit hash

## Refresh mode

Re-fetch stale sources and update changed content.

1. Read `manifest.yaml`
2. For each source, check if `fetched` date + `freshness-ttl` has elapsed
3. For stale sources:
   - Re-fetch the raw content
   - Re-normalize to markdown
   - Compute new content hash
   - If hash changed: replace the source file, update manifest entry
   - If hash unchanged: update only `fetched` date
4. Update `refreshed` date in manifest
5. If any content changed, regenerate `synthesis.md`
6. Append a `history` entry with `event: refreshed`, `sources-changed: M`, and `commit: "--"` placeholder
7. Commit and stamp (same dual-commit pattern as Create step 5):
   - **Commit A**: `git commit -m "research(<trove-id>): refresh N sources (M changed)"`
   - Capture `TROVE_HASH=$(git rev-parse HEAD)`
   - **Commit B**: back-fill hash in history entry, update referencing artifact(s) frontmatter — check `referenced-by` in manifest for all dependents
8. Report: "Refreshed N sources. M had changed content, K were unchanged. New hash: `<TROVE_HASH:0:7>`."

For sources with `freshness-ttl: never`, skip them during refresh.

## Discover mode

Help the user find existing troves relevant to their topic.

1. Scan `docs/troves/*/manifest.yaml` for all troves
2. Match against the user's query by:
   - **Tag match** — trove tags contain query keywords
   - **Title match** — trove ID slug contains query keywords
3. For each match, show: trove ID, tags, source count, last refreshed date, referenced-by list
4. If no matches, suggest creating a new trove

## Graceful degradation

The skill references capabilities generically. When a capability isn't available:

| Capability | Fallback |
|-----------|----------|
| Web search | Skip search-based sources. Tell user: "No web search capability available — provide URLs directly or add a search MCP." |
| Browser / page fetcher | Try basic URL fetch. If that fails: "Can't fetch this URL — paste the content or provide a local file." |
| Media transcription | "No transcription capability available — provide a pre-made transcript file, or add a media conversion tool." |
| Document conversion | "Can't convert this file type — provide a markdown version, or add a document conversion tool." |

Never fail the entire run because one capability is missing. Collect what you can, skip what you can't, and report clearly.

## Capability detection

Before collecting sources, check what's available. Look for tools matching these patterns — the exact tool names vary by installation:

- **Web search**: tools with "search" in the name (e.g., `brave_web_search`, `bing-search-to-markdown`)
- **Page fetching**: tools with "fetch", "webpage", "browser" in the name (e.g., `fetch_content`, `webpage-to-markdown`, `browser_navigate`)
- **Media transcription**: tools with "audio", "video", "youtube" in the name (e.g., `audio-to-markdown`, `youtube-to-markdown`)
- **Document conversion**: tools with "pdf", "docx", "pptx", "xlsx" in the name (e.g., `pdf-to-markdown`, `docx-to-markdown`)

Report available capabilities at the start of collection so the user knows what will and won't work.

## Linking from artifacts

Artifacts reference troves in frontmatter:

```yaml
trove: websocket-vs-sse@abc1234
```

The format is `<trove-id>@<commit-hash>`. The commit hash pins the trove to a specific version — troves evolve over time as sources are added or refreshed, and the hash ensures reproducibility.

The dual-commit workflow in Create step 5, Extend step 8, and Refresh step 7 handles this automatically — Commit A records the trove content and Commit B stamps the hash into the history entry and referencing artifact's frontmatter. Do not defer this to the operator.
