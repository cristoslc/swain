---
title: "Batch Repository Ingestion for swain-search"
artifact: SPEC-051
track: implementable
status: Proposed
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
type: feature
parent-epic: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Batch Repository Ingestion for swain-search

## Problem

When swain-search needs to pull raw source code from a git repository into an evidence pool, it currently does so file-by-file using individual Read and Write tool calls. For the cognee-meta-skill pool, ingesting 9 grouped source files from ~17 raw Python files took >10 minutes because:

1. Each Read tool call has dispatch latency (~2-5s per call)
2. Each Write tool call has similar latency
3. The agent must compose each output file (frontmatter + concatenated content) in context
4. Total: ~26+ sequential tool calls at ~15-20s each = 7-10 minutes of pure tool overhead
5. The agent also spent tokens reasoning about file grouping and content composition

A shell script doing the same work (clone, read, concatenate, write, hash) would complete in <5 seconds.

## Proposed Solution

Add a `scripts/batch-repo-ingest.sh` script to swain-search that:

1. **Accepts**: repo URL, branch, source path within repo, output directory, and a grouping config (YAML or inline)
2. **Clones**: shallow clone to tmp
3. **Groups**: reads files and concatenates them by logical module (per grouping config)
4. **Normalizes**: adds frontmatter (source-id, title, type, path, url, fetched, hash) to each group
5. **Hashes**: computes SHA-256 for each output file
6. **Outputs**: normalized source files to the evidence pool's `sources/` directory
7. **Returns**: JSON manifest fragment with entries for each new source

The agent would then call this script once via Bash, getting all sources created in a single tool call, and append the manifest fragment to `manifest.yaml`.

## Grouping Config

The script should accept a grouping config that maps output slugs to file glob patterns:

```yaml
groups:
  - slug: src-client
    title: "Raw Source — client.py"
    files: ["client.py"]
  - slug: src-execute-observe
    title: "Raw Source — execute.py + observe.py"
    files: ["execute.py", "observe.py"]
  - slug: src-models
    title: "Raw Source — models/"
    files: ["models/*.py"]
```

If no grouping config is provided, default to one source per file.

## Acceptance Criteria

1. Script reduces repo-to-evidence-pool time from >10 minutes to <30 seconds for typical repos
2. Output files match the normalization format in `references/normalization-formats.md`
3. SHA-256 hashes are computed and included in output
4. Script handles: missing files gracefully, binary file exclusion, large file truncation
5. swain-search SKILL.md updated to reference the script for repo ingestion use cases
6. Works with any git repo (public or authenticated via gh/ssh)

## Non-Goals

- Replacing the existing per-source normalization for web pages, media, etc. — only repo/local file batch ingestion
- Automatic grouping heuristics (user or agent provides the grouping config)

## Implementation Notes

- Script should be POSIX sh compatible (runs in the skill's `scripts/` dir)
- Use `git clone --depth 1 --branch` for efficiency
- Clean up tmp clone after completion
- The agent's role shrinks to: (a) decide the grouping config, (b) call the script, (c) update manifest + synthesis
