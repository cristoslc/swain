---
title: "Readability checker scores markdown syntax as prose"
artifact: SPEC-289
type: bug
track: deliverable
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-epic:
linked-artifacts:
  - SPEC-194
depends-on-artifacts: []
---

# Readability checker scores markdown syntax as prose

## Problem

`readability-check.sh` (SPEC-194) inflates Flesch-Kincaid grades by scoring markdown syntax that humans never read as sentences. This causes well-written artifacts to fail the grade-10 threshold, leading to counterproductive "readability edits" that strip useful context.

Observed on EPIC-068 and ADR-036 — both scored 11-14 despite clear, concise prose.

## Root causes

Two stripping gaps in the Python section of `readability-check.sh`:

### 1. Markdown link regex breaks on parentheses in paths

Line 111 uses `\[([^\]]*)\]\([^)]*\)` to strip link URLs. Swain artifact paths contain literal parentheses:

```markdown
[ADR-019](../../adr/Superseded/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md)
```

The `[^)]*` group terminates at the first `)` inside the directory name, leaving the rest of the URL as scored prose. Words like `Project`, `Root`, `Script`, `Convention` from the path all count toward the grade.

### 2. Bare file paths not in backticks scored as prose

Paths like `.agents/scripts/swain/<script>` in body text (not wrapped in backticks) are scored. The slash-separated segments parse as multi-syllable words, inflating the grade. This commonly appears in success criteria, scope lists, and ADR decision sections.

## Acceptance criteria

- [ ] AC1: Markdown links with parentheses in URLs are fully stripped. The link text is kept; the entire URL (up to the balanced closing paren) is removed.
- [ ] AC2: Bare file paths matching common patterns (`./`, `../`, `.agents/`, `skills/`, `docs/`, `bin/`, or any segment containing `.md`, `.sh`, `.py`, `.yaml`, `.json`) are stripped from scored content.
- [ ] AC3: ADR-036 and EPIC-068 both score at or below grade 10 without any prose changes.
- [ ] AC4: Existing passing files still pass (no regression).

## Implementation notes

For AC1, replace the simple link regex with a balanced-paren-aware approach:

```python
# Handle nested parens in URLs: [text](url(with)parens)
content = re.sub(r'\[([^\]]*)\]\([^()]*(?:\([^()]*\))*[^()]*\)', r'\1', content)
```

For AC2, add a path stripping pass after inline code removal:

```python
# Strip bare file paths (slash-separated segments with extensions or dotfiles)
content = re.sub(r'(?<!\[)`?\.?[\w./-]*(?:/[\w.<>*-]+){2,}`?', '', content)
```

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Discovered while authoring ADR-036 and EPIC-068. |
