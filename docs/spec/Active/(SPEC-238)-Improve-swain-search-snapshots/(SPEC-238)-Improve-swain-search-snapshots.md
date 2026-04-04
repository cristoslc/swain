---
title: "Improve swain-search snapshot evidence"
artifact: SPEC-238
track: Active
status: Active
author: cristos
created: 2026-04-02
last-updated: 2026-04-02
parent-vision: VISION-004
priority-weight: medium
linked-artifacts:
  - SPEC-079
  - SPEC-200
---

# Improve swain-search snapshot evidence

## Strategic Direction

`swain-search` is meant to collect high-fidelity evidence from external sources, not just summarize whatever an agent happens to read. A recent incident confirmed this gap: a light agent ran `swain-search`, saw a Google Doc link, read the doc in the browser (without officially exporting it), and treated the resulting summary as the source artifact. That left no traceable raw snapshot, no normalized text, and no verification that the downstream skill was quoting an authoritative copy.

This SPEC closes that gap by defining how `swain-search` downloads, normalizes, and records raw snapshots before any summarization or tagging happens. The workflow must leverage the writing-skills or skill-creator skills to ensure every addition to `skills/` or shared references follows the established documentation rigour. The result is a reproducible audit trail: each evidence pull now records the exported file, its normalization steps, and the skill used to capture it.

## Key Outcomes

- `swain-search` downloads remote documents (Google Docs, slides, etc.) via their export APIs before any summarization, storing the snapshots under `.agents/search-snapshots/`.
- Normalized snapshots are passed through the writing-skills or skill-creator workflows so the resulting markdown follows the same standards as other documented skills (frontmatter, readability checks, citations).
- The evidence pipeline logs the raw file location, export mode, timestamp, and the writing skill/skill-creator command that normalized it, producing structured metadata consumed by `swain-session` and downstream retrospectives.
- Lightweight agents cannot declare a source as "collected" unless a download+normalization record exists; `swain-search` warns when it only scraped a browser summary.

## Requirements

1. **Snapshot exporter** – `swain-search` must detect when a source is a Google Doc, drive link, or similar and invoke the corresponding export endpoint (PDF or plain-text). The export step should be retried against transient failures and fall back to a browser-export helper only when supported APIs fail.
2. **Normalization contract** – Each downloaded snapshot is normalized to markdown via either `writing-skills` or `skill-creator`. The agent must call the relevant skill with the snapshot path, capture the resulting normalized file path, and record the skill invocation in the evidence log.
3. **Metadata logging** – For every snapshot, record `{source_url, export_mode, export_timestamp, normalization_skill, normalized_path, digest}` in `.agents/search-snapshots/metadata.jsonl`.
4. **Evidence validation gate** – When `swain-search` reports a new source, require the presence of the metadata entry before the source qualifies as “downloaded.” If only a summarized version exists, emit a warning that the source is unverified and skip publishing its content downstream.
5. **Documentation and automation** – Update `skills/swain-search/SKILL.md` and any related references with the new workflow, explicitly referencing writing-skills/skill-creator in the procedure. Add a regression test under `skills/swain-search/tests/` that simulates the export+normalization flow and asserts the metadata file contains the correct entries.

## Verification

- Run the new regression test (e.g., `bash skills/swain-search/tests/test-export-snapshot.sh`) to ensure exported snapshots always generate metadata.
- Exercise a `swain-search` run against a Google Doc URL in a controlled environment; confirm `.agents/search-snapshots` contains both the raw export and the normalization log entry.
- Update `docs/superpowers/specs/` or an equivalent manual to describe how to use writing-skills/skill-creator when extending `swain-search`, and verify `readability-check.sh` passes on the new sections.
