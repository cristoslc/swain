---
title: "Agent Runtime I/O Compatibility for Mobile Bridge"
artifact: SPIKE-064
track: container
status: Abandoned
superseded-by: SPIKE-065
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
question: "For each target agent runtime, what I/O mode (structured API, headless JSON, or terminal-only) is available, and can a chat bridge consume it to provide a mobile-native experience?"
gate: Pre-Epic
parent-initiative: INITIATIVE-018
risks-addressed:
  - Building a brittle TUI parser when structured I/O exists
  - Committing to a runtime that lacks headless mode and forces degraded mobile UX
  - Over-engineering an abstraction layer when runtimes share similar structured output
  - Runtimes with interactive or subscription-based auth that cannot run headless without operator presence
evidence-pool: ""
---

# Agent Runtime I/O Compatibility for Mobile Bridge

## Summary

*Populated on completion.*

## Question

For each target agent runtime, what I/O mode is available? Can a chat bridge turn that output into a good mobile experience?

### Context

The operator wants to run agentic work sessions from a phone. Raw terminal output on a small vertical screen is ugly and hard to use. Agent runtimes show prompts, tool-use approvals, and progress updates. These need to appear as chat messages, not as tiny terminal frames.

Two ways to bridge runtime output to chat:

1. **Structured I/O** — the runtime sends JSON events (tool calls, approvals, results). The bridge turns these into chat messages. Clean, but the runtime must support it.
2. **TUI parsing** — the bridge reads terminal output and spots patterns (like `[Y/n]` prompts). It turns those into chat elements. Works with any process, but breaks easily.

This spike maps which runtimes support which mode, and what adapter work each one needs.

## Go / No-Go Criteria

- **Go (structured-first):** Two or more target runtimes offer headless or JSON output. Build the bridge around structured events. Fall back to TUI parsing for terminal-only runtimes.
- **Go (TUI-parsing):** Most runtimes are terminal-only, but their prompts follow fewer than 10 distinct patterns. Build a pattern-matching bridge. Fall back to raw text when parsing fails.
- **No-Go (rethink):** Runtimes differ too much. Structured modes are immature. TUI patterns vary too widely to parse. The bridge idea may not work without upstream changes.

## Pivot Recommendation

If no-go: pick the one runtime with the best structured I/O and use only that for mobile. Or contribute headless-mode support upstream to the runtime you use most.

## Method

### 1. Inventory target runtimes

List every agent runtime the operator might use. Start with:

- Claude Code (Anthropic)
- Gemini CLI (Google)
- Crush CLI
- aider
- OpenCode
- Codex CLI (OpenAI)
- llm CLI (Simon Willison)
- Any runtime launchable via Ollama-backed tools

### 2. Classify I/O mode per runtime

For each runtime, find out:

| Attribute | What to look for |
|-----------|-----------------|
| **Headless mode** | Does it have `--headless`, `--json`, an SDK, or similar? |
| **Output format** | What does the output look like? (tool calls, approvals, results, errors) |
| **Input model** | How do you send input? (stdin, API call, file watch, callback) |
| **Prompts** | What does it ask the user? (permissions, tool approval, model choice) |
| **Auth model** | How does it log in? (subscription, API key, OAuth, local config) |
| **Swain support** | Does it read AGENTS.md? SKILL.md? Support MCP? |

### 3. Test structured I/O where available

For runtimes with a headless or JSON mode:

- Launch in headless mode in a swain-enabled repo
- Capture output for a simple task ("read the README and summarize")
- Document the event schema (fields, types, how prompts appear)
- Try sending input back through the structured channel

### 4. Test TUI parsing where needed

For terminal-only runtimes:

- Launch in a pty (via `pyte` or `script`)
- Capture output for the same simple task
- List the interactive patterns (prompts, confirms, progress bars)
- Check pattern consistency: can a regex or state machine catch them?
- Test `pyte` (Python terminal emulator) to read escape sequences as data

### 5. Build compatibility matrix

Fill in this table:

| Runtime | I/O Mode | Output Format | Input Model | Prompt Patterns | Adapter Work | Auth | Swain Depth |
|---------|----------|--------------|-------------|-----------------|-------------|------|-------------|
| Claude Code | ? | ? | ? | ? | ? | Max sub | Full |
| Gemini CLI | ? | ? | ? | ? | ? | Google auth | AGENTS.md + SKILL.md |
| ... | | | | | | | |

### 6. Assess bridge feasibility

- How many event types must the bridge handle?
- Can one adapter interface cover both structured and parsed events?
- How much adapter code does each runtime need?
- When parsing fails, what does the user see? (raw text in a code block)

## Time Box

2 sessions. Session one: inventory and classify via docs and quick launches. Session two: hands-on tests of the top 3-4 runtimes.

## Deliverables

1. Filled-in compatibility matrix
2. Sample structured output from runtimes that support it
3. Pattern catalog for TUI-only runtimes (regex, confidence level)
4. Recommendation: structured-first, TUI-first, or hybrid
5. Draft adapter interface (pseudocode) for how the bridge would read events

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-06 | -- | Created from INITIATIVE-018 discussion; operator-requested |
| Abandoned | 2026-04-18 | — | Blank template; superseded by SPIKE-065 (Complete) |

Abandoned: blank template. Superseded by SPIKE-065 (Complete) which contains the actual research findings.
