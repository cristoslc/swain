---
source-id: "016"
title: "python-frontmatter — Parse and edit YAML frontmatter in markdown files"
type: web
url: "https://pypi.org/project/python-frontmatter/"
fetched: 2026-03-15T03:05:00Z
hash: "pending"
---

# python-frontmatter

Standard Python library for parsing YAML frontmatter from markdown files. Used widely in static site generators and documentation tools.

## Key characteristics

- **Simple API**: `frontmatter.load(file)` returns a Post object with `.metadata` (dict) and `.content` (str)
- **Round-trip safe**: `frontmatter.dump(post, file)` preserves content while updating frontmatter
- **Field access**: `post['status']`, `post.get('track', 'default')`
- **Supports multiple handlers**: YAML (default), TOML, JSON frontmatter

## Usage for frontmatter diffing

```python
import frontmatter

# Cache previous state
cached = frontmatter.load('docs/spec/SPEC-014.md')
old_status = cached.get('status')

# On file change event, re-parse
updated = frontmatter.load('docs/spec/SPEC-014.md')
new_status = updated.get('status')

if old_status != new_status:
    # Lifecycle transition detected
    emit_transition_event(path, old_status, new_status)
```

## Relevance to reactive loop

python-frontmatter is the right tool for the frontmatter cache + diff layer. On each file change event from watchfiles, swain re-parses the frontmatter, compares to the cached state, and emits a transition event only when the configured column_field (e.g., `status`) actually changed. This filters out body-only edits, metadata-only changes, and phantom events.
