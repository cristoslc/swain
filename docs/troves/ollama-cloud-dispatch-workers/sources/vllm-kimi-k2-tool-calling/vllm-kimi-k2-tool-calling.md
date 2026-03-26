---
source-id: "vllm-kimi-k2-tool-calling"
title: "Chasing 100% Accuracy: Debugging Kimi K2 Tool-Calling on vLLM"
type: web
url: "https://vllm.ai/blog/Kimi-K2-Accuracy"
fetched: 2026-03-25T18:00:00Z
hash: "27b1bf64b1d600af384c115287effc8ff536004cbfe70b975d8b387e11dddec9"
---

# Chasing 100% Accuracy: Debugging Kimi K2 Tool-Calling on vLLM

Deep technical investigation by the vLLM team into why Kimi K2's tool calling had only an 18% success rate initially, and how they achieved a 4.4x improvement.

## Root Causes

### Problem 1: Missing `add_generation_prompt` Parameter

vLLM's security design inspects function signatures and only passes explicitly defined arguments. Kimi's tokenizer accepted `add_generation_prompt` via `**kwargs`, but vLLM discarded it. Without this parameter, the model received truncated prompts that prevented it from knowing whether to generate a tool call, text reply, or structured response.

### Problem 2: Empty Content Field Handling

vLLM automatically converts empty string content (`''`) into a list structure (`[{'type': 'text', 'text': ''}]`). Kimi's Jinja-based chat template expected string input, causing literal list representations (`"[{'type': 'text', 'text': ''}]"`) to be inserted into prompts — creating malformed formatting.

### Problem 3: Overly Strict ID Parser

The tool-call parser used `functions.func_name:idx` format splitting. When historical conversation data contained non-compliant IDs like `search:2`, the parser threw `IndexError` and discarded valid tool calls.

## Key Takeaway

> "The `chat_template` is the critical handshake between a model and its serving framework. When integrating a new model, meticulously validate every piece of its template logic against the framework's specific behaviors and assumptions."

## Performance Impact

- Initial: 218 successful tool calls from 1,200+ attempts (18% success)
- After fixes: 971 successful calls (4.4x improvement)
- Remaining failures: model hallucination rather than parsing failures

## Relevance to Ollama Cloud

Each model family needs its own tool call parser. vLLM maintains dedicated parsers per model (`kimi_k2_tool_parser.py`, etc.). Ollama handles this via its `RENDERER`/`PARSER` template system, but the same class of bugs — template mismatches, format assumptions, content type handling — applies to any serving framework including Ollama Cloud.
