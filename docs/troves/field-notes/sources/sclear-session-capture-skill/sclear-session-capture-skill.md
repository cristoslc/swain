---
source-id: "sclear-session-capture-skill"
title: "Claude Code /sclear skill — session capture & clear devlog"
type: web
url: "https://gist.github.com/shines/1c280094c4e12276b2d5345178987c36"
fetched: 2026-03-22T12:00:00Z
hash: "b33daa10a9ed11f0c98e4505455ab0775be3b39bc598b7587818dd3d9de9c9a1"
---

# Claude Code /sclear skill — session capture & clear devlog

A Claude Code skill that captures session evolution as a devlog entry before clearing the conversation. Published as a GitHub Gist by `shines`.

## Skill metadata

- **Name:** sclear
- **Description:** Capture session evolution as a devlog entry, then clear. Use when the user wants to end a session but preserve what happened — decisions, pivots, learnings, and narrative hooks for future writing.
- **Model invocation disabled:** yes (no LLM calls during clear — pure extraction)
- **Allowed tools:** `Bash(git *)`, `Bash(date *)`, `Bash(ls *)`, `Bash(mkdir *)`, `Write`, `Read`, `Glob`, `Grep`

## Workflow

### Step 1: Determine the project

- Check current working directory
- Look at what files were discussed or changed
- Derive a short kebab-case project slug (e.g., `website`, `work`, `play`)
- If session spanned multiple projects or was general, use `general`

### Step 2: Gather context

- Run `git diff --stat` and `git log --oneline -5` (to see what changed)
- Run `git status` to see uncommitted work
- Review the conversation for decisions, pivots, surprises, and unfinished threads

### Step 3: Write the devlog entry

**Location:** `~/.claude/devlogs/{project-slug}/YYYY-MM-DD-HHMMSS.md`

**Structure:**

```markdown
---
date: {ISO 8601 timestamp}
project: {project name}
session_id: {if available}
---

## What was the intent?
{Why did the user start this session?}

## What actually happened?
{Brief narrative of the arc — not a transcript}

## Decisions made
{Bulleted list with rationale}

## Pivots & surprises
{What changed direction. The most valuable section for future writing.}

## Current state
{What's done, half-done, blocked}

## Next moves
{What the user would likely do next session}

## The interesting part
{If this were a blog post, what's the hook? One paragraph max.}
```

### Writing guidelines

- Be honest and specific, not performative
- Include actual file names, function names, error messages
- Keep under 400 words total
- Write in first person from the user's perspective

### Safety rules

- Do NOT clear if any write or verification step fails
- Read back the file to verify before clearing
- Tell user the file path and summary before clearing

## Interesting design choices

1. **disable-model-invocation: true** — the skill runs without LLM reasoning during the clear phase, relying purely on extraction tools. This is unusual and suggests performance/cost optimization for what's essentially a structured data extraction task.

2. **Devlog as blog raw material** — the explicit framing of session capture as "raw material for future blog posts" gives the devlog entries a dual purpose: session continuity AND content pipeline. The "interesting part" section is specifically designed to surface blog-worthy hooks.

3. **First-person voice** — writing from the user's perspective rather than the agent's creates devlog entries that read as personal notes rather than agent reports.

4. **Narrative over transcript** — the emphasis on capturing the "arc" and "pivots" rather than a blow-by-blow is a strong editorial choice that prioritizes future utility over completeness.

5. **Fail-safe clearing** — multiple verification gates before the destructive `/clear` action, with explicit instructions to stop and inform the user on any failure.
