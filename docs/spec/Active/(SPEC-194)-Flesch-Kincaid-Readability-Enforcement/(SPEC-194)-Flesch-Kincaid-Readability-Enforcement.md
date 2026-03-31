---
title: "Flesch-Kincaid Readability Enforcement"
artifact: SPEC-194
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-30
last-updated: 2026-03-30
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Flesch-Kincaid Readability Enforcement

## Problem Statement

Swain artifacts differ in how easy they are to read. The result depends on which agent or prompt wrote them. Long sentences and jargon creep in with no way to catch them. There is no automated check — clarity is left to chance.

## Desired Outcomes

All swain artifacts read at or below a 9th-grade level. Readers spend less time parsing dense prose. Agents only rewrite text when the score is too high. Text that already passes stays as-is.

## External Behavior

### readability-check.sh

**Inputs:**
- One or more markdown file paths as positional arguments
- `--threshold N` flag (default: 9) to override the grade-level ceiling
- `--json` flag for machine-readable output

**Preprocessing:**
The script strips non-prose content before scoring:
- YAML frontmatter (between `---` fences)
- Fenced code blocks (``` and ~~~ blocks)
- Inline code (backtick spans)
- Mermaid and diagram blocks
- Markdown tables (`|...|` lines)
- URLs and image links
- HTML tags

**Scoring:**
Runs `uv run --with textstat python3` to score with the Flesch-Kincaid grade-level formula.

**Outputs (stdout):**
```
PASS  docs/specs/SPEC-192.md  grade=7.2
FAIL  docs/epics/EPIC-042.md  grade=11.4
SKIP  docs/adr/ADR-003.md     words=32
```

- `PASS` — prose scores at or below the threshold
- `FAIL` — prose exceeds the threshold
- `SKIP` — fewer than 50 words of prose remain after stripping (not enough to score)

**Exit codes:**
- `0` — all files PASS or SKIP
- `1` — one or more files FAIL

**JSON mode (`--json`):**
```json
[
  {"file": "docs/specs/SPEC-192.md", "result": "PASS", "grade": 7.2, "words": 342},
  {"file": "docs/epics/EPIC-042.md", "result": "FAIL", "grade": 11.4, "words": 510},
  {"file": "docs/adr/ADR-003.md", "result": "SKIP", "grade": null, "words": 32}
]
```

### Governance rule (AGENTS.content.md)

A new section in the governance source. It says all artifacts must score FK grade 9 or below. Agents run `readability-check.sh` after writing an artifact. They revise only when the score is too high.

### Readability protocol (references/readability-protocol.md)

A shared reference doc for skills that produce artifacts. It covers:
- When to run the check (after the body is done, before commit)
- How to invoke the script
- What to do on FAIL (shorter sentences, simpler words, active voice)
- A cap of 3 rewrite tries — after that, note the score and move on
- SKIP needs no action

## Acceptance Criteria

1. **Given** a file with FK grade <= 9, **when** the script runs, **then** it prints `PASS` with the grade and exits 0.

2. **Given** a file with FK grade > 9, **when** the script runs, **then** it prints `FAIL` with the grade and exits 1.

3. **Given** a file with fewer than 50 prose words after stripping, **when** the script runs, **then** it prints `SKIP` and exits 0.

4. **Given** a file with frontmatter, code blocks, tables, and inline code, **when** the script strips non-prose content, **then** none of it affects the FK score.

5. **Given** `--threshold 12`, **when** a file scores grade 11, **then** the script prints `PASS`.

6. **Given** `--json`, **when** the script runs, **then** output is valid JSON matching the schema above.

7. **Given** two files where one fails and one passes, **when** the script runs, **then** it reports both and exits 1.

8. **Given** AGENTS.content.md after this spec ships, **when** an agent reads the rules, **then** it finds the readability section with the grade 9 target.

9. **Given** `readability-protocol.md` exists, **when** a skill checks for guidance, **then** the doc provides the invocation pattern, rewrite rules, and the 3-attempt cap.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** The script, the governance rule, and the protocol doc.
- **Out of scope:** Pre-commit hooks, scoring old artifacts, grammar checks beyond FK grade, skill file changes (skills read the rule from AGENTS.md).
- **Dependency:** `uv` must be on the system (already required per CLAUDE.md).
- **No new project deps** — `textstat` runs via `uv run --with textstat`, not installed project-wide.

## Implementation Approach

Three deliverables, in order:

1. **readability-check.sh** — Shell script in `.agents/bin/`. Strips frontmatter, code, and tables, then pipes prose to `uv run --with textstat`. Supports `--threshold`, `--json`, and multi-file input. Outputs PASS/FAIL/SKIP per file.

2. **Governance rule** — A "Readability" section in AGENTS.content.md, next to the existing ADR compliance and skill change sections. Propagated to AGENTS.md.

3. **readability-protocol.md** — Shared reference doc in `skills/swain-design/references/`. Covers when to run, how to invoke, rewrite steps on failure, and the 3-attempt cap.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | _pending_ | Initial creation |
