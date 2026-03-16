# Normalization Formats

Every source in a trove is normalized to a markdown file with YAML frontmatter. The frontmatter schema is consistent across types; the body structure varies by source type.

## Common frontmatter

All normalized source files share this frontmatter:

```yaml
---
source-id: "mdn-websocket-api"
title: "Source Title"
type: web | forum | document | media | local | repository | documentation-site
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
- Timestamps in `[MM:SS]` or `[HH:MM:SS]` format
- Speaker labels on every speaker change (or every few minutes for single-speaker)
- Include a "Key Points" section auto-extracted from the content
- For podcasts with multiple speakers, clearly attribute each segment

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
