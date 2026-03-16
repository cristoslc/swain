# Manifest Schema

Each trove has a `manifest.yaml` at its root that tracks trove metadata, source provenance, and freshness configuration.

## Top-level fields

```yaml
# Required
trove: <trove-id>                  # Slug identifier (matches directory name)
created: <ISO date>                # When the trove was first created
refreshed: <ISO date>              # When any source was last fetched or refreshed
tags:                              # For trove discovery by other artifacts
  - <tag>

# Optional
freshness-ttl:                     # Per-source-type defaults (override at source level)
  web: 7d                          # Web pages — default 7 days
  forum: 7d                        # Forum threads — default 7 days
  document: 30d                    # PDFs, DOCX, local files — default 30 days
  media: never                     # Video/audio transcripts — content doesn't change
  repository: 30d                  # Git repositories — default 30 days
  documentation-site: 7d           # Documentation sites — default 7 days

referenced-by:                     # Back-links to artifacts using this trove
  - artifact: SPIKE-001
    commit: abc1234                # Commit where the reference was added
  - artifact: ADR-003
    commit: def5678

sources:                           # Ordered list of collected sources
  - <source entry>                 # See below
```

## Source entry fields

```yaml
# Required
source-id: "mdn-websocket-api"    # Slug-based ID (used as directory name)
type: web | forum | document | media | local | repository | documentation-site
fetched: <ISO datetime>            # When this source was last fetched
title: "WebSocket API - MDN"       # Source title

# Required for remote sources
url: "https://..."                 # Original URL

# Required for local sources
path: "path/to/file.pdf"          # Relative to project root

# Optional
hash: "a1b2c3d4e5f6..."          # Bare hex SHA-256 digest (no sha256: prefix)
freshness-ttl: 14d                 # Per-source override
duration: "45:32"                  # For media sources — total duration
speakers:                          # For media sources — identified speakers
  - "Alice"
  - "Bob"
highlights: []                     # Paths relative to source-id directory — key files worth reading first
selective: false                   # True if only a subset of the source was ingested (large repos/sites)
notes: "Focused on section 3"     # Freeform annotation
```

## Source types

| Type | What it covers | Default TTL |
|------|---------------|-------------|
| `web` | Web pages, documentation, blog posts, API docs | 7 days |
| `forum` | Forum threads, discussions, Q&A sites, GitHub issues | 7 days |
| `document` | PDFs, DOCX, PPTX, XLSX, local markdown | 30 days |
| `media` | Video, audio, podcasts (transcribed) | never |
| `local` | Local files already in markdown | 30 days |
| `repository` | Git repositories — tree structure preserved | 30 days |
| `documentation-site` | Documentation sites — section hierarchy preserved | 7 days |

## Freshness TTL format

Duration strings: `<number><unit>` where unit is `d` (days), `w` (weeks), `m` (months), or `never`.

Examples: `7d`, `2w`, `1m`, `never`

## Content hashing

The `hash` field stores a bare hex SHA-256 digest of the normalized markdown content (not the raw source). On refresh:

1. Re-fetch the raw source
2. Re-normalize to markdown
3. Compare SHA-256 of new normalized content to stored hash
4. If changed: update the source file, hash, and `fetched` date
5. If unchanged: update only `fetched` date (confirms source is still valid)

## Example manifest

```yaml
trove: websocket-vs-sse
created: 2026-03-09
refreshed: 2026-03-09
tags:
  - real-time
  - websocket
  - sse
  - server-sent-events

freshness-ttl:
  web: 14d
  media: never

referenced-by:
  - artifact: SPIKE-001
    commit: abc1234

sources:
  - source-id: mdn-websocket-api
    type: web
    url: "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"
    fetched: 2026-03-09T14:30:00Z
    title: "WebSocket API - MDN Web Docs"
    hash: "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"

  - source-id: whatwg-sse-spec
    type: web
    url: "https://html.spec.whatwg.org/multipage/server-sent-events.html"
    fetched: 2026-03-09T14:31:00Z
    title: "Server-sent events - HTML Standard"
    hash: "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"

  - source-id: strangeloop-2025-realtime-patterns
    type: media
    url: "https://youtube.com/watch?v=xyz"
    fetched: 2026-03-09T15:00:00Z
    title: "Real-time Web Patterns - StrangeLoop 2025"
    hash: "g7h8i9a1b2c3d4e5f6g7h8i9a1b2c3d4e5f6g7h8i9a1b2c3d4e5f6g7h8i9a1b2"
    duration: "42:15"
    speakers:
      - "Jamie Zawinski"
    highlights:
      - "strangeloop-2025-realtime-patterns.md"
```
