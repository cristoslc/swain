# Normalization Formats

Every source in a trove is normalized to a markdown file with YAML frontmatter. The frontmatter schema is consistent across types; the body structure varies by source type.

## Snapshot-first normalization contract (SPEC-220)

For remote documents (especially Google Docs/Drive links), normalization is not allowed until a raw snapshot is exported first.

Required sequence:
1. Export/download raw file:
   - `bash skills/swain-search/scripts/export-snapshot.sh --url "<source-url>" --out-dir ".agents/search-snapshots/raw"`
2. Normalize via `writing-skills` or `skill-creator` using the downloaded file path.
3. Log the evidence record:
   - `bash skills/swain-search/scripts/log-snapshot-metadata.sh --source-url "<source-url>" --export-mode "<mode>" --raw-path "<raw-path>" --normalized-path "<normalized-path>" --normalization-skill "<writing-skills|skill-creator>"`
4. Verify source eligibility:
   - `bash skills/swain-search/scripts/verify-snapshot-evidence.sh --source-url "<source-url>"`

If step 4 fails, the source is unverified and must not be published into trove synthesis.

## Common frontmatter

All normalized source files share this frontmatter:

```yaml
---
source-id: "mdn-websocket-api"
title: "Source Title"
type: web | forum | document | media | local | repository | documentation-site | x-thread
url: "https://..."           # or path for local sources
fetched: 2026-03-09T14:30:00Z
hash: "a1b2c3..."
---
```

## Web pages

Strip navigation, ads, sidebars, footers, and cookie banners. Preserve the main content area with its heading structure.

```markdown
---
source-id: "mdn-websocket-api"
title: "WebSocket API - MDN Web Docs"
type: web
url: "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"
fetched: 2026-03-09T14:30:00Z
hash: "a1b2c3..."
---

# WebSocket API - MDN Web Docs

[Main content with original heading hierarchy preserved]

[Code blocks preserved with language tags]

[Tables preserved in markdown format]
```

Key rules:
- Preserve heading hierarchy (h1-h6 -> # through ######)
- Preserve code blocks with language annotation
- Preserve tables
- Convert images to `![alt text](url)` — keep alt text, keep URL
- Remove inline scripts, styles, tracking pixels
- Remove "related articles", "see also" sections unless substantive

## Forum threads / discussions

Preserve chronological structure with author attribution and timestamps.

```markdown
---
source-id: "hn-websocket-vs-sse-dashboards"
title: "WebSocket vs SSE for real-time dashboards"
type: forum
url: "https://news.ycombinator.com/item?id=12345"
fetched: 2026-03-09T14:35:00Z
hash: "d4e5f6..."
participants:
  - "user_alpha"
  - "user_beta"
  - "user_gamma"
post-count: 15
---

# WebSocket vs SSE for real-time dashboards

## user_alpha — 2026-03-01 10:15 UTC

[Original post content]

## user_beta — 2026-03-01 10:42 UTC

> [quoted text from parent, as blockquote]

[Reply content]

## user_gamma — 2026-03-01 11:03 UTC

[Reply content]
```

Key rules:
- Each post is an h2 with `author — timestamp`
- Quoted/reply content uses blockquotes (`>`)
- Preserve code blocks within posts
- Omit deleted/removed posts (note their absence if the thread references them)
- For nested threads (Reddit-style), flatten to chronological with reply-to attribution

## X/Twitter threads

X threads are a source type of their own. Each one has an author, a post count, and a post-by-post order. Cited tweets appear inline. The `fetch_x_thread.py` script unrolls the thread via `api.fxtwitter.com`. It also resolves cited posts and self-replies. The output keeps every post verbatim.

```markdown
---
source-id: "schlickw-us-foreign-policy-anthropic-mythos"
title: "US Foreign Policy and the Anthropic Mythos"
type: x-thread
url: "https://x.com/schlickw/status/1234567890"
fetched: 2026-04-13T14:30:00Z
hash: "k1l2m3..."
author-handle: "schlickw"
author-name: "Example Author"
author-url: "https://x.com/schlickw"
published-date: "2026-04-12T18:00:00Z"
tweet-count: 14
---

# US Foreign Policy and the Anthropic Mythos

## Full Thread

1. [[1/14]](https://x.com/schlickw/status/1234567890) Opening post text, verbatim, with [@mentions](https://x.com/mention) and [#tags](https://x.com/hashtag/tag) hyperlinked inline.

2. [[2/14]](https://x.com/schlickw/status/1234567891) Second post text with a citation to another thread:

   > **[@other_author](https://x.com/other_author)** ([2026-04-10](https://x.com/other_author/status/9876543210)): Cited post text, verbatim.
   >
   > Continuation from the cited author's self-reply, appended as context.
   > _Linked: [article-title](https://example.com/article) — one-sentence synopsis._

3. [[3/14]](https://x.com/schlickw/status/1234567892) Third post text...
```

Key rules:
- Strip leading auto-mention chains. These are the `@handle` prefixes X adds to reply posts. They are threading artifacts, not the author's words.
- Hyperlink every `@mention` inline as `[@handle](https://x.com/handle)`. Hyperlink hashtags as `[#tag](https://x.com/hashtag/tag)`.
- Render cited posts as indented blockquotes under the citing post. Use this format: `> **[@handle](url)** ([date-link](tweet_url)): <verbatim text>`.
- Append up to 3 substantive self-replies from the cited author as blockquote continuation. Skip bare-URL self-replies. They already live in `external_links`. Link out if more than 3 exist.
- Resolve external links inside cited posts when the `article`, `external_links`, or `photos` fields point to longer content. Add a one-sentence synopsis as a sub-blockquote.
- No timestamps. X threads have no internal timeline.
- If the response is a single post on a known thread-opener, record the entry as `failed: true` and `reason: x-thread-unrollable`. Do not write a source file.

## Documents (PDF, DOCX, PPTX, XLSX)

Convert to markdown preserving structure. Use available document conversion capabilities.

```markdown
---
source-id: "q4-2025-arch-review"
title: "Q4 2025 Architecture Review"
type: document
path: "docs/reviews/q4-2025-arch-review.pdf"
fetched: 2026-03-09T15:00:00Z
hash: "g7h8i9..."
page-count: 12
---

# Q4 2025 Architecture Review

[Converted content with heading structure preserved]

[Tables preserved in markdown]

[Figures noted as: **[Figure 1: System architecture diagram]**]
```

Key rules:
- Preserve heading hierarchy from the document structure
- Preserve tables (convert to markdown tables)
- Note figures/images with descriptive captions: `**[Figure N: description]**`
- For spreadsheets: convert each sheet to a markdown table with the sheet name as heading
- For presentations: each slide becomes a section with the slide title as heading

## Media (video / audio transcripts)

Transcribe with timestamps and speaker labels when available.

```markdown
---
source-id: "strangeloop-2025-realtime-patterns"
title: "Real-time Web Patterns - StrangeLoop 2025"
type: media
url: "https://youtube.com/watch?v=xyz"
fetched: 2026-03-09T15:30:00Z
hash: "j0k1l2..."
duration: "42:15"
speakers:
  - "Jamie Zawinski"
transcript-source: vtt   # vtt | caption | vision-ocr | local-ocr
---

# Real-time Web Patterns - StrangeLoop 2025

**Duration:** 42:15
**Speaker(s):** Jamie Zawinski

## Transcript

**[00:00]** Jamie Zawinski: Welcome everyone. Today I want to talk about...

**[02:15]** So the first pattern we'll look at is long polling...

**[15:30]** Now, WebSockets solve many of these problems, but they introduce new ones...

## Key Points

- [Auto-extracted key points from the transcript]
- [Major arguments, conclusions, recommendations]
```

Key rules:
- Timestamps in `[MM:SS]` or `[HH:MM:SS]` format — only when `transcript-source: vtt`.
- Speaker labels on every speaker change (or every few minutes for single-speaker).
- Include a "Key Points" section auto-extracted from the content.
- For podcasts with multiple speakers, clearly attribute each segment.
- The `transcript-source` field records which tier produced the text. Omit `duration` and `speakers` when caption, vision-ocr, or local-ocr was used (those tiers do not recover that metadata).

## Local files (already markdown)

Minimal transformation — add frontmatter, verify structure.

```markdown
---
source-id: "internal-api-design-notes"
title: "Internal API Design Notes"
type: local
path: "docs/notes/api-design.md"
fetched: 2026-03-09T16:00:00Z
hash: "m3n4o5..."
---

[Original file content, unchanged]
```

Key rules:
- Add frontmatter if missing
- Do not modify the content body
- Hash is computed on the original content (for change detection)

## Repositories

Mirror the repository tree structure under the source directory. Preserve directory hierarchy.

```
sources/express-framework/
  express-framework.md          # Summary/index file with frontmatter
  lib/
    router/
      index.js
      route.js
    application.js
  package.json
```

The index file (`<source-id>.md`) contains:

```markdown
---
source-id: "express-framework"
title: "Express.js Framework"
type: repository
url: "https://github.com/expressjs/express"
fetched: 2026-03-09T16:30:00Z
hash: "p6q7r8..."
highlights:
  - "lib/application.js"
  - "lib/router/index.js"
selective: true
---

# Express.js Framework

Repository overview and structure summary.
```

Key rules:
- Mirror directory tree faithfully
- For large repos, set `selective: true` and only ingest key files
- Populate `highlights` with the most important files
- The index `.md` file provides the frontmatter and a structural overview

## Documentation sites

Mirror the section hierarchy under the source directory. Preserve navigation structure.

```
sources/react-docs/
  react-docs.md                 # Summary/index file with frontmatter
  getting-started/
    installation.md
    tutorial.md
  api-reference/
    hooks/
      useState.md
      useEffect.md
```

The index file (`<source-id>.md`) contains:

```markdown
---
source-id: "react-docs"
title: "React Documentation"
type: documentation-site
url: "https://react.dev/learn"
fetched: 2026-03-09T17:00:00Z
hash: "s9t0u1..."
highlights:
  - "api-reference/hooks/useState.md"
  - "getting-started/tutorial.md"
selective: true
---

# React Documentation

Site structure and section overview.
```

Key rules:
- Mirror section hierarchy from the site navigation
- Preserve internal links where possible (adjust to relative paths)
- For large sites, set `selective: true` and focus on relevant sections
- Populate `highlights` with the most important pages
