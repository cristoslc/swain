# Synthesis: Ollama Cloud as Dispatch Worker Backend

## Key Findings

### Tool calling is the critical integration point — and it's fragile

The #1 technical risk for Ollama Cloud dispatch workers is not model intelligence but **tool calling reliability**. Agent frameworks like OpenCode require models to return structured `tool_calls` objects in the OpenAI format. Three independent failure modes can prevent this:

1. **Context window starvation** — Ollama defaults to ~4K context, which silently breaks tool calling since tool definitions alone can consume thousands of tokens. Cloud models may have different defaults, but the failure is the same: "prompt too long" errors or truncated prompts that prevent the model from generating structured responses. (opencode-ollama-tool-issues, ollama-cloud-api-direct-testing)

2. **Model-specific parser mismatches** — Each model family (Qwen, Mistral, DeepSeek, GLM, Kimi) uses different output formats for tool calls (`<tool_call>`, `[TOOL_CALLS]`, `<|tool▁calls▁begin|>`, etc.). Ollama's RENDERER/PARSER system translates these to the OpenAI-compatible format, but bugs in the translation layer cause raw tags to leak through as text content. (ollama-tool-calling-architecture, vllm-kimi-k2-tool-calling)

3. **Intermittent thinking-tag interference** — Models with reasoning/thinking capabilities (qwen3.5, kimi-k2) can intermittently emit tool calls as raw text when thinking tags interleave with tool call generation. This was confirmed as an Ollama bug in versions 0.17.6–0.18.2. (qwen35-tool-call-printing-bug)

### Ollama Cloud's API does return proper OpenAI-format tool calls — for some models

Direct API testing (SPIKE-045, 2026-03-25) confirmed that `qwen3.5:397b` and `glm-5` return correctly structured `tool_calls` responses through the `/v1/chat/completions` endpoint. The format matches the OpenAI spec: `id`, `type: "function"`, `function.name`, `function.arguments` as a JSON string, and `finish_reason: "tool_calls"`.

However, `kimi-k2.5` is completely broken on Ollama Cloud — returning "prompt too long" errors on trivial prompts, suggesting a server-side misconfiguration. (ollama-cloud-api-direct-testing)

### Authentication is simple and API-key-based

Bearer token auth via API key — no interactive login, no subscription management, no 1Password dance. This makes Ollama Cloud ideal for headless dispatch workers. (awesomeagents-ollama-cloud-review, devto-beginners-guide-ollama-cloud)

### OpenCode + Ollama has a known, widespread reliability problem

Multiple OpenCode GitHub issues (#1068, #3029, #5694, #1034) document that Ollama models frequently fail to execute tool calls in OpenCode's agent loop. The community has identified workarounds (custom Modelfiles, explicit `num_ctx` settings, version pinning), but there is no "just works" configuration. (opencode-ollama-tool-issues)

### Model quality is adequate for mechanical tasks

Available models (qwen3.5:397b, glm-5, deepseek-v3.1:671b) score well on tool-calling benchmarks. GLM-4.5 achieved 90.6% tool-calling success in benchmarks. These models are sufficient for mechanical tasks (frontmatter edits, xref updates, script generation) but likely insufficient for complex design decisions. (medium-ollama-cloud-api-ready, awesomeagents-ollama-cloud-review)

### Performance and pricing are viable for background work

42–95 tok/s on shared tier. Free tier: $10/month credits (~30K requests). Pro: $20/month. For background dispatch workers that run asynchronously, throughput matters more than latency. The free tier covers development; Pro covers light production. (devto-beginners-guide-ollama-cloud)

## Points of Agreement

All sources confirm:
- OpenAI-compatible API at `ollama.com/v1/`
- Bearer token auth via API key
- Tool calling is supported but model-dependent
- Context window configuration is critical for tool calling

## Points of Disagreement

- **Cloud vs local reliability**: Some sources report better tool calling on cloud (server manages templates); others report worse (no version control, no Modelfile customization)
- **Model selection**: Community is split on whether coding-specific models (qwen3-coder, devstral) or general models (kimi-k2, glm-5) are better for agentic tool use

## Gaps

- **No end-to-end test of Ollama Cloud models driving a multi-step file-editing agent session** — all tool-calling tests are single-turn; the spike's trial protocol is the first multi-step test
- **Intermittent failure rate unknown** — the qwen3.5 tool-call-printing bug is intermittent; we don't know the failure rate over 100+ tool calls in a single session
- **OpenCode config for Ollama Cloud** — no documented working configuration for `@ai-sdk/openai-compatible` + Ollama Cloud + tool calling (community configs are all for local Ollama)
- **Rate limit behavior under sustained tool use** — unknown how Ollama Cloud handles rapid sequential API calls from an agent loop
