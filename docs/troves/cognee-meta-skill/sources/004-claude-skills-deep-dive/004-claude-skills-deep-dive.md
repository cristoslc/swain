---
source-id: "004"
title: "Claude Agent Skills: A First Principles Deep Dive"
type: web
url: "https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/"
fetched: 2026-03-15T21:06:00Z
hash: "sha256:placeholder"
---

# Claude Agent Skills: A First Principles Deep Dive

Technical deep dive into Claude Agent Skills' prompt-based meta-tool architecture, covering context injection design, two-message patterns, LLM-based routing, and runtime context modification.

## SKILL.md Structure & Frontmatter

**Two-Part Design:** YAML frontmatter (configuration) + Markdown content (instructions).

**Required fields:** `name` (identifier), `description` (primary signal for skill selection).

**Optional fields:** `allowed-tools` (comma-separated permissions), `model` (override), `license`, `version`, `disable-model-invocation`, `mode`.

**Resource bundling:** `/scripts/` (executable automation), `/references/` (text docs loaded via Read), `/assets/` (templates referenced by path).

Recommended: keep instructions under 5,000 words to avoid context bloat.

## Two-Message Pattern

**Dual-message architecture:**
1. **Message 1 (Visible, isMeta: false):** Minimal XML metadata — `<command-message>`, `<command-name>`, `<command-args>`. User-facing status indicator.
2. **Message 2 (Hidden, isMeta: true):** Full skill prompt (500-5,000 words). Sent to API but excluded from UI.

Using `role: "user"` with `isMeta: true` makes the skill prompt appear as user input to Claude, keeping it temporary and localized to the current interaction. This solves the transparency-vs-clarity tradeoff.

## Routing — Pure LLM Reasoning

No algorithmic routing. System formats all available skills into `<available_skills>` section in Skill tool description. Each skill listed as: `"skill-name": description - when_to_use`. Claude reads and decides via transformer-based reasoning.

**Progressive disclosure:** Only names and descriptions load initially. Full SKILL.md loads only after selection — prevents context bloat while maintaining discoverability.

## Runtime Context Modification

Skills yield a `contextModifier` that transforms the execution environment:
1. **Tool permissions:** Pre-approves tools in `allowed-tools` without user confirmation
2. **Model override:** Switches model if specified in frontmatter

Modifications persist only during skill execution — no residual behavioral changes.

## Permission Scoping

Allowed tools injected into `toolPermissionContext.alwaysAllowRules`. Supports wildcard patterns: `Bash(git:*)`, `Bash(npm:*)`.

Security: list only necessary tools. "If you're just reading and writing files, `Read,Write` is sufficient."

## Design Patterns

1. **Script automation:** Execute Python/Bash from `/scripts/`
2. **Read-process-write:** Load → transform → write
3. **Search-analyze-report:** Grep patterns → read → analyze → report
4. **Command chain:** Sequential dependent commands
5. **Wizard-style:** User confirmation between steps
6. **Template-based:** Fill templates from `/assets/`
7. **Iterative refinement:** Multiple analysis passes
8. **Context aggregation:** Combine info from multiple sources
