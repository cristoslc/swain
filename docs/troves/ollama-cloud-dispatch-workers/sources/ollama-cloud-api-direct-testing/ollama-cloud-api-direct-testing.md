---
source-id: "ollama-cloud-api-direct-testing"
title: "SPIKE-045 Direct API Testing — Tool Calling Format Verification"
type: local
url: "local://spike-045-direct-testing"
fetched: 2026-03-25T18:00:00Z
hash: "4a458f5a068a668553a22a4d73fd0a7c6c381952b1cc402af8d0e7dbfa9f7a9c"
---

# SPIKE-045 Direct API Testing — Tool Calling Format Verification

First-party testing of Ollama Cloud's OpenAI-compatible API for tool calling support, conducted 2026-03-25 as part of SPIKE-045.

## Test Setup

Direct `curl` calls to `https://ollama.com/v1/chat/completions` with Bearer token auth. Tool definition:

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Read the contents of a file at the given path",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "The file path to read"}
      },
      "required": ["path"]
    }
  }
}
```

Prompt: "Use the read_file tool to read the contents of /tmp/test.txt"

## Results

### kimi-k2.5 — BROKEN

Every request (with or without tools, even "Say hello") returns:

```json
{"error": "prompt too long; exceeded max context length by 59432 tokens"}
```

For comparison, `kimi-k2-thinking` handles the same "Hi" prompt at 8 prompt tokens. The k2.5 model appears to have a misconfigured context window or system prompt inflation on Ollama Cloud's infrastructure. This is a server-side bug, not a tool-calling format issue.

### qwen3.5:397b — WORKS

Returns properly structured OpenAI-format tool calls:

```json
{
  "message": {
    "role": "assistant",
    "content": "",
    "reasoning": "The user wants me to read...",
    "tool_calls": [{
      "id": "call_rokyupd6",
      "index": 0,
      "type": "function",
      "function": {
        "name": "read_file",
        "arguments": "{\"path\":\"/tmp/test.txt\"}"
      }
    }]
  },
  "finish_reason": "tool_calls"
}
```

All fields match OpenAI format. `finish_reason` correctly set to `"tool_calls"`. Arguments are a JSON string, not an object. Includes a `reasoning` field (non-standard but harmless — ignored by OpenAI-compatible clients).

### glm-5 — WORKS

Same correct format as qwen3.5:397b. Also includes `reasoning` field. Properly sets `finish_reason: "tool_calls"`.

## Key Observations

1. **Ollama Cloud's OpenAI-compatible endpoint correctly returns structured `tool_calls`** for models that support it (qwen3.5, glm-5). The format matches the OpenAI spec.

2. **kimi-k2.5 is completely broken** on Ollama Cloud as of 2026-03-25 — not just for tool calling, but for all inference. This is distinct from the tool-calling format issues documented in vLLM and local Ollama setups.

3. **The `reasoning` field** is a non-standard extension in the response. OpenAI-compatible clients should ignore unknown fields, but poorly implemented clients might choke on it.

4. **Token counts vary significantly** between models for the same prompt: qwen3.5 used 332 prompt tokens vs glm-5's 185. This suggests different system prompt sizes or tokenizer differences.

## OpenCode Trial Correlation

The kimi-k2.5 trial failure (18 seconds, raw `<tool_call>` tags in output) aligns with this finding. OpenCode likely received the "prompt too long" error, and the visible output was the model's attempt to generate text before the error was surfaced — or OpenCode's fallback text rendering of a failed API call.
