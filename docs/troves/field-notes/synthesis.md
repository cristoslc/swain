# Field Notes — Synthesis

A catch-all trove for interesting references, patterns, and data points that don't have an immediate purpose or artifact context but might be useful later. Items here may eventually get refiled into purpose-specific troves or inspire new work.

## Session capture patterns

**Source:** [sclear-session-capture-skill](sources/sclear-session-capture-skill/sclear-session-capture-skill.md)

A Claude Code skill that captures session state as structured devlog entries before `/clear`. Notable design choices:

- **Dual-purpose capture:** session continuity AND content pipeline (explicitly framed as "raw material for future blog posts")
- **Narrative extraction over transcription:** captures the arc, pivots, and surprises — not a blow-by-blow. The "interesting part" section forces identification of the blog-worthy hook.
- **disable-model-invocation:** runs without LLM reasoning during extraction, using only file tools. Unusual and worth studying — suggests extraction can be purely structural.
- **Fail-safe clearing:** multiple verification gates before the destructive action

### Relevance to swain

The devlog structure overlaps with swain-retro but serves a different audience — personal reflection and content creation rather than project governance. The "pivots & surprises" and "interesting part" sections are editorial choices that swain-retro could adopt. The first-person voice and 400-word limit are worth considering for retro docs that currently have no length discipline.

## Gaps

- No other session capture tools collected yet for comparison
- No data points on devlog-to-blog-post conversion rates or editorial workflows
