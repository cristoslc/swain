---
source-id: "qwen35-tool-call-printing-bug"
title: "qwen3.5 Sometimes Prints Tool Calls Instead of Executing Them (Ollama #14745)"
type: web
url: "https://github.com/ollama/ollama/issues/14745"
fetched: 2026-03-25T18:00:00Z
hash: "611c1ce277e84b189c1b986c334cfa97eaf220cd4e76eb824db8c4937ee4d607"
---

# qwen3.5 Sometimes Prints Tool Calls Instead of Executing Them

Ollama GitHub issue #14745 documenting an intermittent bug where qwen3.5 outputs raw tool call XML instead of structured tool_calls in the API response.

## Problem

Using qwen3.5:9b with OpenCode 1.2.24 on Ollama 0.17.6+, the model intermittently outputs tool calls as raw text:

```
<tool_call><function=bash>...<parameter=command>grep "redacted" | head -20</parameter>...
```

Instead of returning structured `tool_calls` in the API response. This halts agent workflows because the framework receives text instead of actionable tool call objects.

## Root Cause

The issue is related to thinking tag open/close handling. When the model's thinking process interleaves with tool call generation, the parser loses track of whether it's inside a thinking block or a tool call block, causing the raw tags to leak through as text content.

## Affected Versions

- Ollama 0.17.6 through 0.18.2 (confirmed broken)
- Regression likely introduced by PR #14605
- Related issues: #14493, #14601

## Workaround

**Downgrade to Ollama 0.17.5** — this version does not exhibit the behavior. Multiple users confirmed the fix.

## Relevance to Ollama Cloud

Ollama Cloud runs its own infrastructure — the specific Ollama version is not user-controlled. If Cloud runs a version with this bug, users have no workaround. This makes cloud-based tool calling less reliable than local Ollama (where version pinning is possible).

The qwen3.5:397b model on Ollama Cloud returned correctly structured tool calls in our direct API testing (SPIKE-045), suggesting either: (a) Cloud runs a fixed version, (b) the bug is specific to smaller model variants, or (c) the bug is intermittent and we didn't hit it in our limited testing.

## Risk for Dispatch Workers

An intermittent tool-calling failure is worse than a consistent one for dispatch workers. A consistent failure can be detected and handled; an intermittent one means some worker sessions will silently fail partway through multi-step operations, leaving artifacts in inconsistent states.
