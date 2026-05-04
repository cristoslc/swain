---
source: composite (GitHub issues)
type: forum
title: "OpenCode todowrite Tool Issues (Aggregated)"
fetched: 2026-04-30
proxy-used: none
---

# OpenCode todowrite Tool Issues

## Issue #10813: Parameter type error (Jan 2026)
- **Problem**: LLM sends `todos` as string instead of array.
- **Error**: `Invalid input: expected array, received string`
- **Status**: Open

## Issue #7512: Stringified JSON (Nov 2025)
- **Problem**: LLM sends stringified JSON for `todos` array, e.g. `todos="[{\"id\":\"1\",...}]"`
- **Root cause**: Tools with typed parameters (array, object) fail when LLM sends string form.
- **Status**: Open

## Issue #1373: Type validation failure (Feb 2025)
- **Problem**: Same stringified-JSON issue with more verbose escaping.
- **Status**: Closed (likely fixed by server-side parsing improvements).

## Issue #12938: Subagent todowrite denial (Jan 2026)
- **Problem**: Subagents cannot use todowrite even when explicitly enabled in agent config.
- **Models affected**: glm-4.7-flash, glm-4.5-air, qwen3-code-next
- **LLM confusion**: Models report todowrite not appearing in their available functions list.
- **Status**: Open

## Issue #234: Tool name casing (Oct 2024)
- **Problem**: Qwen models generate `Write` (capital W) instead of `write`.
- **Error**: `AI_NoSuchToolError: Model tried to call unavailable tool 'Write'`
- **Broader finding**: Open-source models have inconsistent tool calling implementations.
- **Suggested fix**: Automatic name normalization (Write → write).
- **Status**: Open

## Issue #11357: Empty params with Kimi K2.5 (Jan 2026)
- **Problem**: `{}` parameter causes strict mode validation failure.
- **Affected**: Kimi K2.5 via Fireworks/Moonshot.
- **Status**: Open
