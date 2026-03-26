---
source-id: "opencode-ollama-tool-issues"
title: "OpenCode + Ollama Tool Calling Issues (GitHub Issues #1068, #3029, #5694)"
type: web
url: "https://github.com/anomalyco/opencode/issues/1068"
fetched: 2026-03-25T18:00:00Z
hash: "ff4de44a3477e68015b9ff872b8c32f378ff146f16fa600b6f22512e4eefee3c"
---

# OpenCode + Ollama Tool Calling Issues

Consolidated findings from three related GitHub issues in the OpenCode repository documenting widespread tool calling failures with Ollama models.

## Issue #1068: Tool use with Ollama models

**Problem:** Models attempt tool calls but executions are aborted. Even with `"tools": true` in config, models fail to reliably execute tool calls.

**Root causes identified:**
1. `num_ctx` parameter in OpenCode config not properly passed to Ollama via the OpenAI-compatible endpoint
2. Model templates not properly configured for tool calling format
3. Not all Ollama models have equal tool calling capability

**Solutions found:**
- Set context window at the Ollama level: `/set parameter num_ctx 16384` then `/save`
- Use `OLLAMA_CONTEXT_LENGTH` environment variable
- Create custom Ollama models with explicit Modelfile templates
- Use only models with documented tool support (Qwen3, Mistral, Devstral)

## Issue #3029: Ollama tool calling issues

**Problem:** Models invoke non-existent tools (`repo_browser.read_file`, `assistant`) instead of the available OpenCode tools (`bash`, `edit`, `read`, `write`, etc.).

**Affected models:** gpt-oss:20b, granite4:micro, various Qwen and Gemma variants — all configured with `"tools": true`.

**Resolution:** Classified as configuration/model capability issue, not an OpenCode bug. Community-developed `ollama-x-opencode` repo provides working configurations.

## Issue #5694: Local Ollama models are not agentic

**Problem:** Ollama models (local and cloud) cannot access files or use tools in OpenCode, while built-in models like BigPickle work correctly.

**Root cause:** Ollama's default `num_ctx` is approximately 4K tokens — far too small for agentic operations that include tool definitions and file context. As one maintainer noted: "They by default give agent like 4k tokens which is unusable for coding."

**Additional finding:** The Ollama OpenAI-compatible endpoint previously didn't allow setting `num_ctx`, and the AI SDK provider didn't support it either. This has since been partially addressed but remains a pain point.

## Cross-cutting Findings

1. **Context window is the #1 blocker** — not tool format, not model intelligence. Ollama defaults to 4K context which silently breaks tool calling.
2. **The `@ai-sdk/openai-compatible` provider** (used by OpenCode) translates between OpenAI and Ollama formats, but context window configuration doesn't pass through cleanly.
3. **Model-specific templates matter** — each model family (Qwen, Mistral, DeepSeek, GLM) has its own tool call output format. Ollama's template system (`RENDERER`/`PARSER`) handles the translation, but cloud models may not have the same template flexibility.
4. **"tools": true in OpenCode config** is necessary but not sufficient. The model must also support tool calling at the template/architecture level, and have adequate context.
