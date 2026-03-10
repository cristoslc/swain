# Manifest Schema

Each evidence pool has a `manifest.yaml` at its root that tracks pool metadata, source provenance, and freshness configuration.

## Top-level fields

```yaml
# Required
pool: <pool-id>                    # Slug identifier (matches directory name)
created: <ISO date>                # When the pool was first created
refreshed: <ISO date>              # When any source was last fetched or refreshed
tags:                              # For pool discovery by other artifacts
  - <tag>

# Optional
freshness-ttl:                     # Per-source-type defaults (override at source level)
  web: 7d                          # Web pages — default 7 days
  forum: 7d                        # Forum threads — default 7 days
  document: 30d                    # PDFs, DOCX, local files — default 30 days
  media: never                     # Video/audio transcripts — content doesn't change

referenced-by:                     # Back-links to artifacts using this pool
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
id: "001"                          # Sequential ID within the pool
slug: "mdn-websocket-api"         # Human-readable slug (used in filename)
type: web | forum | document | media | local
fetched: <ISO datetime>            # When this source was last fetched
title: "WebSocket API - MDN"       # Source title

# Required for remote sources
url: "https://..."                 # Original URL

# Required for local sources
path: "path/to/file.pdf"          # Relative to project root

# Optional
hash: "sha256:abc123..."          # Content hash for change detection on refresh
freshness-ttl: 14d                 # Per-source override
duration: "45:32"                  # For media sources — total duration
speakers:                          # For media sources — identified speakers
  - "Alice"
  - "Bob"
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

## Freshness TTL format

Duration strings: `<number><unit>` where unit is `d` (days), `w` (weeks), `m` (months), or `never`.

Examples: `7d`, `2w`, `1m`, `never`

## Content hashing

The `hash` field uses SHA-256 of the normalized markdown content (not the raw source). On refresh:

1. Re-fetch the raw source
2. Re-normalize to markdown
3. Compare SHA-256 of new normalized content to stored hash
4. If changed: update the source file, hash, and `fetched` date
5. If unchanged: update only `fetched` date (confirms source is still valid)

## Example manifest

```yaml
pool: websocket-vs-sse
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
  - id: "001"
    slug: mdn-websocket-api
    type: web
    url: "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"
    fetched: 2026-03-09T14:30:00Z
    title: "WebSocket API - MDN Web Docs"
    hash: "sha256:a1b2c3..."

  - id: "002"
    slug: whatwg-sse-spec
    type: web
    url: "https://html.spec.whatwg.org/multipage/server-sent-events.html"
    fetched: 2026-03-09T14:31:00Z
    title: "Server-sent events - HTML Standard"
    hash: "sha256:d4e5f6..."

  - id: "003"
    slug: tech-talk-realtime-patterns
    type: media
    url: "https://youtube.com/watch?v=xyz"
    fetched: 2026-03-09T15:00:00Z
    title: "Real-time Web Patterns - StrangeLoop 2025"
    hash: "sha256:g7h8i9..."
    duration: "42:15"
    speakers:
      - "Jamie Zawinski"
```
