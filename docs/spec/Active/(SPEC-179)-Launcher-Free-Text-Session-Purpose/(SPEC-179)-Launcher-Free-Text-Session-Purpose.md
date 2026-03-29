---
title: "Launcher Free-Text Session Purpose"
artifact: SPEC-179
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: ""
type: enhancement
parent-epic: EPIC-045
parent-initiative: ""
linked-artifacts:
  - SPEC-172
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Launcher Free-Text Session Purpose

## Problem Statement

The `swain` shell launcher function accepts no arguments. The operator must start a session and then separately communicate context. Typing `swain new bug about timestamps` should capture "new bug about timestamps" as session purpose text and pass it through to swain-session, where it becomes the initial bookmark or context note.

## Desired Outcomes

The operator can provide session intent at launch time without quotes or special syntax. This text flows through to swain-session and is visible immediately, reducing the friction of establishing session context.

## External Behavior

**Input:** `swain <free text>` at the terminal — e.g., `swain new bug about x, y, and z`.

**Precondition:** The `swain()` shell function is installed (via swain-init launcher templates).

**Output:** The agentic CLI starts with `/swain-session` as the initial prompt, and the free text is available to swain-session as session purpose. swain-session writes it as the initial bookmark note.

**Constraint:** Free text is unquoted and may contain commas, spaces, and shell-safe punctuation. The launcher must not require the operator to wrap arguments in quotes.

## Acceptance Criteria

- **AC-1:** Given the operator types `swain fix the broken timestamp`, when the session starts, then swain-session receives "fix the broken timestamp" as purpose text.
- **AC-2:** Given free text with commas and spaces (e.g., `swain new bug about x, y, and z`), the full string is captured without truncation or word splitting.
- **AC-3:** Given no free text (just `swain`), the launcher behaves exactly as it does today — no regression.
- **AC-4:** All launcher templates (claude/zsh, claude/bash, claude/fish, and other runtimes) are updated consistently.
- **AC-5:** swain-session detects the incoming purpose text and writes it as the session bookmark note.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- All launcher templates in `skills/swain-init/templates/launchers/` must be updated.
- swain-session SKILL.md must document how it receives and uses the purpose text.
- The mechanism for passing text varies by runtime CLI (Claude Code uses `--prompt` or initial prompt concatenation). Each runtime template handles it per its CLI interface.
- Fish shell uses `$argv` instead of `$@`.
- No changes to the `swain-init` detection/recommendation logic — only the templates and swain-session handling.

## Implementation Approach

1. Update launcher templates to capture `$@` (or `$argv` for fish) and append it to the CLI invocation. For Claude Code: `claude --dangerously-skip-permissions "/swain-session" --prompt "Session purpose: $*"` or concatenate into the initial prompt string.
2. Update swain-session SKILL.md to detect purpose text (e.g., from `--prompt` argument or environment variable) and write it as the initial bookmark.
3. Test with multi-word, comma-containing input to verify no truncation.
4. Test bare `swain` invocation to verify no regression.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
