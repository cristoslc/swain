---
source-id: "ollama-tool-calling-architecture"
title: "Ollama Tool Calling Architecture — Native vs OpenAI-Compatible"
type: web
url: "https://deepwiki.com/ollama/ollama/7.2-tool-calling-and-function-execution"
fetched: 2026-03-25T18:00:00Z
hash: "970fb30aa54a8bbdef59d56325b8df292ba8fd938f23409cfbb0024210bab527"
---

# Ollama Tool Calling Architecture

Technical analysis of how Ollama handles tool calling internally, based on DeepWiki's source code analysis.

## Tool Definition Rendering

Tools are passed to models via the `{{ .Tools }}` template variable. Different model families format tools distinctly:

- **Qwen models**: `<tool_call>{...}</tool_call>`
- **Mistral**: `[TOOL_CALLS][...]`
- **DeepSeek**: `<|tool▁calls▁begin|>...`
- **JSON models**: Direct object/array notation

The `RENDERER` and `PARSER` directives in Ollama Modelfiles control how tool definitions are injected into prompts and how tool call responses are extracted from model output.

## Tool Call Parsing

The `tools.Parser` uses a state machine approach to extract tool invocations from streaming model output:

1. Detects model-family-specific tags (e.g., `<tool_call>` for Qwen)
2. Extracts and validates JSON arguments
3. Maintains a buffer for incomplete tool calls across stream chunks
4. Validates tool names against available tools
5. Tool arguments use `orderedmap.Map` for deterministic serialization

## Native `/api/chat` vs OpenAI-Compatible `/v1/chat/completions`

| Aspect | Native | OpenAI-Compatible |
|--------|--------|-------------------|
| Endpoint | `/api/chat` | `/v1/chat/completions` |
| Tool call format | Ollama's `ToolCall` struct | OpenAI-format with `id`, `type`, `function` |
| Arguments | Ordered map (preserves order) | JSON string (loses order) |
| Translation | None | Middleware in `openai.go` |
| `type` field | Not included | Always `"function"` |

The OpenAI compatibility middleware in `openai.go` performs bidirectional conversion. This means:

1. OpenAI-format tool definitions in the request are converted to Ollama's internal format
2. Ollama's tool call responses are converted back to OpenAI format
3. The conversion should be transparent — but edge cases (empty content, special tokens, streaming chunks) can cause mismatches

## Implications for Agent Frameworks

Agent frameworks using the `@ai-sdk/openai-compatible` provider (like OpenCode) rely on the `/v1` endpoint. They never see Ollama's native format — they only interact with the OpenAI-compatible layer. This means:

1. Tool calling works **if and only if** Ollama's per-model parser correctly extracts tool calls from the model's output
2. If the parser fails (wrong tags, malformed JSON, context overflow), the framework receives plain text instead of structured `tool_calls`
3. The framework has no way to recover — it sees the model as "not wanting to use tools" when in reality the serving layer failed to parse the tool call
