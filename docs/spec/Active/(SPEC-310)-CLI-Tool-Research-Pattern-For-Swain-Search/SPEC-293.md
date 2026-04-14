---
id: SPEC-310
title: "CLI Tool Research Pattern for swain-search"
artifact: SPEC-310
track: implementable
status: Active
author: operator
created: 2026-04-07
last-updated: 2026-04-07
priority-weight: medium
type: enhancement
parent-epic: 
parent-initiative: 
linked-artifacts: 
depends-on-artifacts: 
addresses: 
evidence-pool: 
source-issue: 
swain-do: required
---

# CLI Tool Research Pattern for swain-search

## Problem Statement

When `swain-search` researches a command-line tool, it does not have a defined pattern for capturing the tool's help resources. This leads to incomplete evidence pools when researching CLI tools. The skill needs a specific research pattern to ensure comprehensive capture of manpages, `--help` output, and subcommand help pages.

## Desired Outcomes

When `swain-search` is used to research a CLI tool, the resulting evidence pool contains complete documentation of the tool's interface including its main help system, manpage, and any subcommand hierarchies. This enables thorough understanding of the tool's capabilities and usage patterns.

## External Behavior

### Inputs
- A CLI tool name or path (e.g., `git`, `gh`, `kubectl`)
- Optional: specific subcommand path (e.g., `git remote`, `gh issue list`)

### Trigger Conditions

This CLI research pattern is activated when the research target exhibits CLI tool characteristics:

- The target exists as an executable in `PATH`
- The target name matches common CLI tool naming patterns (e.g., no spaces, lowercase-with-hyphens or single words)
- The research context indicates a command-line tool (explicit mention, tool already known to be CLI, etc.)

When these conditions are met, `swain-search` should apply the full CLI research pattern described below.

### Required Research Pattern for CLI Tools

When `swain-search` receives a research request for a CLI tool, it must execute the following capture sequence:

1. **Manpage Capture**
   - Attempt `man <tool-name>` and capture output
   - If `man` page exists, normalize to markdown and add as a source

2. **Primary Help Capture**
   - Execute `<tool-name> --help` and capture output
   - Execute `<tool-name> -h` as fallback if available
   - Normalize output to markdown and add as a source

3. **Subcommand Discovery**
   - Parse help output using the following indicators to identify subcommands:
     - Explicit "Commands:" or "Subcommands:" section headings (case-insensitive)
     - Indented command names listed under a "Usage:" or "Commands:" section
     - Common subcommand patterns in usage lines (e.g., `<tool> <command> [options]` where `<command>` is a known subcommand name)
     - Indented bullet or numbered lists of commands
   - Only treat a candidate as a subcommand if it:
     - Is a single word or hyphen-separated lowercase string
     - Appears as a positional argument in usage syntax
     - Is NOT already a flag (starts with `-` or `--`)
   - If subcommands are detected, recursively capture help for each subcommand
   - Execute `<tool-name> <subcommand> --help` and normalize to markdown

4. **Additional Help Resources**
   - Capture any `help`, `usage`, or informational output from standard patterns like:
     - `<tool-name> help <command>`
     - `<tool-name> <command> -h`
     - `<tool-name> <command> --help`

### Output
- All captured content normalized to markdown
- Stored as sources in the evidence pool with appropriate labels (e.g., "manpage", "help output", "subcommand help")

### Edge Cases
- If `man` page does not exist, proceed with `--help` capture only
- If `--help` fails, attempt `-h` as final fallback
- If all help capture attempts fail, note the failure in the evidence pool
- For tools with deep subcommand hierarchies (e.g., `git status` vs `git remote show`), capture up to 2 levels deep by default

## Acceptance Criteria

| ID | Criterion |
|----|----------|
| AC-1 | Given a CLI tool with an available manpage, when swain-search researches it, then the manpage is captured and normalized to markdown |
| AC-2 | Given a CLI tool, when swain-search researches it, then the `--help` output is captured and normalized to markdown (falling back to `-h` if `--help` is unavailable) |
| AC-3 | Given a CLI tool with subcommands, when swain-search researches it, then each subcommand's help is recursively discovered and captured |
| AC-4 | Given a tool with nested subcommands (depth > 1), when swain-search researches it, then help is captured up to 2 levels deep |
| AC-5 | Given all help capture attempts fail for a tool, when swain-search researches it, then the failure is noted in the evidence pool |
| AC-6 | Given captured help content, when the research is complete, then all content is normalized to markdown and stored as labeled sources |

## Scope & Constraints

### In Scope
- Implementing the research pattern in `swain-search`
- Manpage capture using system `man` command
- `--help` and `-h` flag capture
- Subcommand discovery algorithm (parse indicators defined in External Behavior)
- Recursive subcommand help capture (up to 2 levels deep)
- Markdown normalization of all captured content
- Evidence pool integration

### Out of Scope
- Interactive terminal capture (TTY-only help content)
- Version-specific help (assumes latest or stable version)
- Platform-specific behavior (limited to POSIX-compliant tools)

## Implementation Approach

1. **Implement Capture Functions**
   - `capture_manpage(tool_name)` — runs `man` and normalizes output
   - `capture_help_flag(tool_name)` — runs `--help` and `-h` fallbacks
   - `discover_subcommands(help_output)` — parses help text using the indicators in External Behavior to find subcommand names
   - `capture_subcommand_help(tool_name, subcommand)` — recursively captures subcommand help

2. **Normalize Content** — Convert captured plain text to markdown (preserve formatting, add code fences)

3. **Store in Evidence Pool** — Label sources appropriately ("manpage", "help-output", "subcommand-help")

4. **Handle Failures Gracefully** — Log failures rather than blocking research

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | - | Moved to Active |
