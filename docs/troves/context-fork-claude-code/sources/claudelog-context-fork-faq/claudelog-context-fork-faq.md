---
source-id: "claudelog-context-fork-faq"
title: "What is Context Fork in Claude Code | ClaudeLog"
type: web
url: "https://claudelog.com/faqs/what-is-context-fork-in-claude-code/"
fetched: 2026-03-16T00:00:00Z
hash: "af22e8c30631fe5a67b24f2d01e2f7e63dcafeec553c4459f3f86b2e83e4277e"
---

# What is Context Fork in Claude Code

## Overview

"Context fork runs skills in an isolated sub-agent context with separate conversation history, preventing skill execution from cluttering your main conversation thread."

## How to Use It

Add `context: fork` to skill frontmatter:

```yaml
---
name: deep-analysis
description: Comprehensive codebase analysis
context: fork
agent: Explore  # Optional: specify agent type
---
```

When invoked, the skill executes in a separate context with independent conversation history and tool access.

## Why Use Context Fork

Skills typically add knowledge to your current conversation, potentially cluttering the main thread with execution details. Context fork isolates skill execution in a sub-agent with separate context, keeping your main conversation focused.

**Benefits:**
- Clean main thread -- skill execution details remain isolated
- Independent context with separate conversation history and tool access
- Focused workflow without implementation details
- Flexible tool access -- forked context can use different tools than the main thread

This approach works particularly well for complex analysis skills that generate extensive output or require multiple execution steps.

## Context Fork vs Alternatives

| Approach | Purpose | Context |
|----------|---------|---------|
| `context: fork` | Isolate skill execution | Separate sub-agent with independent history |
| Task tool | Parallel processing | Sub-agents for concurrent operations |
| Skills (default) | Add knowledge | Current conversation context |

Use context fork for skills generating extensive output, requiring multiple steps, or benefiting from isolated execution without cluttering the main conversation.
