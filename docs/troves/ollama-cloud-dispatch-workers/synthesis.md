# Synthesis: Ollama Cloud as Dispatch Worker Backend

## Key Findings

### Ollama Cloud is a viable alternative backend for dispatch workers

Ollama Cloud (public beta since January 2026) provides OpenAI-compatible API endpoints (`https://ollama.com/v1/chat/completions`) with Bearer token authentication. This means any agent framework that speaks the OpenAI API can use Ollama Cloud without a Claude Code subscription or Anthropic API key. Workers authenticate with an `OLLAMA_API_KEY` environment variable — no interactive login required.

### Authentication is simple and API-key-based

1. Create an account at ollama.com
2. Generate an API key at `ollama.com/settings`
3. Set `OLLAMA_API_KEY` environment variable or pass `Authorization: Bearer <key>` header
4. No interactive login, no browser auth flow, no subscription management

This makes Ollama Cloud ideal for headless dispatch workers — no 1Password, no browser-based OAuth, no subscription login dance.

### `ollama launch` enables zero-config coding agent startup

The `ollama launch` command can start coding agents directly:
- `ollama launch opencode` — open-source coding assistant (no proprietary auth needed)
- `ollama launch codex` — OpenAI's Codex CLI
- `ollama launch claude-code` — still requires Anthropic auth (not useful for auth-free workers)

OpenCode is the most relevant for swain dispatch: it's open-source, reads AGENTS.md, and connects to Ollama Cloud via the OpenAI-compatible API.

### Model quality is a real tradeoff

Available coding-capable models include `qwen3-coder:480b-cloud`, `deepseek-v3.1:671b-cloud`, `devstral-2:123b-cloud`, and `gpt-oss:120b-cloud`. These are strong open-source models, but none match Claude's quality for complex agentic work (multi-step artifact creation, spec authoring, design reasoning). They're suitable for:
- Mechanical tasks (xref fixes, frontmatter updates, script generation)
- Code implementation from detailed plans
- Search and normalization work

They're likely insufficient for:
- Complex design decisions
- Spec authoring requiring deep project context
- Multi-artifact coordination

### Performance is the bottleneck

Shared inference: 42-95 tok/s (2-13x slower than competitors). Cold starts on niche models: 10-15 seconds. No SLA on shared tier. Dedicated endpoints ($0.80+/hr) bring latency to competitive levels (~210 tok/s).

For dispatch workers that run in the background, throughput matters more than latency. A 2x slowdown is acceptable if the worker runs asynchronously; a 13x slowdown is painful even for background work.

### Free tier is limited but usable for development

$10/month credits (~30K requests) with hourly and weekly rate limits. Pro tier at $20/month, Max at $100/month. For a solo developer dispatching occasional background workers, the free tier covers development; Pro covers light production use.

## Points of Agreement

All sources confirm:
- OpenAI-compatible API at `ollama.com/v1/`
- Bearer token auth via API key
- 400+ models including large cloud-only variants
- Seamless local-to-cloud workflow
- Free tier available

## Points of Disagreement

- **Quality sufficiency**: some sources treat cloud models as production-ready; the benchmark review shows significant quality and speed gaps vs. Claude/GPT-4
- **Auth model**: one source suggests multiple accounts for key rotation to bypass rate limits, which is against spirit of ToS

## Gaps

- **No source tests Ollama Cloud with swain-like agentic workflows** — all sources focus on single-turn or simple multi-turn conversations, not multi-step file-editing agent sessions
- **Context window limitations** — OpenAI API spec through Ollama defaults to ~2K context; must create custom Modelfiles with `num_ctx` for production use, and it's unclear if this works with cloud models
- **Tool calling reliability** — only deepseek-v3.1 and gpt-oss models support tool calling; reliability for complex tool chains is untested
- **AGENTS.md compliance** — no source confirms whether OpenCode or other agents consistently read and follow AGENTS.md conventions when backed by Ollama Cloud models

## Relevance to swain-dispatch

**swain-dispatch is deprecated** (requires ANTHROPIC_API_KEY with per-token billing). Ollama Cloud could enable a different dispatch model:

1. Workers run OpenCode or similar open agent with Ollama Cloud backend
2. Workers read AGENTS.md and follow swain conventions
3. Workers authenticate with Ollama API key (no Claude subscription)
4. Workers handle mechanical/implementation tasks; operator handles design decisions

**Open questions for a spike:**
- Does OpenCode reliably follow AGENTS.md governance when backed by qwen3-coder or deepseek?
- Can cloud models handle swain's artifact format (YAML frontmatter, lifecycle tables)?
- What's the effective context window for cloud models via the OpenAI API?
- Is the free/Pro tier rate limit sufficient for a dispatch workload?
