---
title: "Ollama Cloud Dispatch Worker Feasibility"
artifact: SPIKE-045
track: container
status: Active
author: operator
created: 2026-03-25
last-updated: 2026-03-25
question: "Can OpenCode + Ollama Cloud (qwen3-coder:480b or deepseek-v3.1:671b) reliably execute a simple swain SPEC — reading AGENTS.md, following conventions, editing files, running tests — making auth-free dispatch workers viable for mechanical tasks?"
gate: Pre-MVP
risks-addressed:
  - "Dispatch workers require Claude Code subscription — limits scaling and increases cost"
  - "No auth-free path for background agent execution"
trove: ollama-cloud-dispatch-workers@71ed4fc
linked-artifacts:
  - INITIATIVE-008
  - ADR-016
---

# Ollama Cloud Dispatch Worker Feasibility

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

Can OpenCode + Ollama Cloud (qwen3-coder:480b or deepseek-v3.1:671b) reliably execute a simple swain SPEC — reading AGENTS.md, following conventions, editing files, running tests — making auth-free dispatch workers viable for mechanical tasks?

## Context

swain-dispatch is deprecated ([ADR-016](../../../adr/Active/(ADR-016)-Deprecate-swain-dispatch.md)) because it required `ANTHROPIC_API_KEY` with per-token billing. Ollama Cloud (public beta since January 2026) offers an OpenAI-compatible API with simple API key auth — no subscription, no interactive login. The `ollama launch opencode` command can start an open-source coding agent backed by Ollama Cloud models, creating a potential path for auth-free dispatch workers under [INITIATIVE-008](../../../initiative/Active/(INITIATIVE-008)-Automated-Work-Intake/(INITIATIVE-008)-Automated-Work-Intake.md) (Automated Work Intake).

Key unknowns: whether open-source models can reliably follow swain's AGENTS.md governance conventions, handle YAML frontmatter artifact formats, and maintain coherent multi-step editing sessions.

## Go / No-Go Criteria

**Go (viable for mechanical dispatch)** — all of:
1. OpenCode + qwen3-coder:480b (or deepseek-v3.1:671b) can read and parse AGENTS.md governance rules
2. The agent correctly identifies and invokes swain skills when prompted (or follows manual instructions equivalent to skill behavior)
3. The agent can complete a simple mechanical SPEC: edit YAML frontmatter, create/modify markdown files, run shell scripts
4. Success rate ≥ 70% across 5 trial runs of the same SPEC
5. Effective context window ≥ 16K tokens (enough to hold AGENTS.md + a SPEC + working files)

**No-Go** — any of:
1. Context window < 8K tokens through the OpenAI-compatible API (breaks AGENTS.md loading)
2. Success rate < 50% on mechanical tasks
3. Agent hallucinates file paths, artifact IDs, or frontmatter fields > 30% of the time
4. Free/Pro tier rate limits prevent completing a single SPEC within 30 minutes

## Pivot Recommendation

If No-Go:
- **Pivot A**: Use Ollama Cloud as inference backend but pair with Claude Code Agent SDK for the agent framework (still needs Anthropic auth but gets Ollama pricing for most calls)
- **Pivot B**: Self-host Ollama with a coding-capable model (qwen3-coder:32b) on a dedicated VPS — removes rate limits and cloud dependency at ~$55/month for an RTX 4090 build
- **Pivot C**: Abandon multi-model dispatch; keep all agent work on Claude Code and focus on reducing per-session cost through model routing (SPIKE-026)

## Test Protocol

### Setup
1. Create an Ollama Cloud account and API key
2. Install OpenCode CLI
3. Configure OpenCode to use `https://ollama.com/v1` as base URL with the API key
4. Select a completed mechanical SPEC as the test case (e.g., a frontmatter fix or xref update)

### Trial Runs (5x per model)
1. Start OpenCode in the swain repo root
2. Prompt: "Read AGENTS.md, then implement SPEC-NNN following swain conventions"
3. Record: did it read AGENTS.md? Did it find the spec? Did it correctly edit files? Did it follow conventions?
4. Score each run: pass (completed correctly), partial (completed with errors), fail (could not complete)

### Models to Test
- `qwen3.5:397b` — 256K context, newest Qwen general model (397B params)
- `glm-5` — 198K context, Zhipu general model
- `deepseek-v3.1:671b` — 160K context, DeepSeek general model (671B params)

**Eliminated models:**
- `kimi-k2.5` — server-side bug on Ollama Cloud; "prompt too long" on trivial prompts (2026-03-25)
- `kimi-k2-thinking` — non-standard tool call IDs (`functions.*:N`), 60-100s latency per tool call

### Measurements
- Context window effective size (can it hold AGENTS.md + spec + files?)
- Time to complete the SPEC
- Token consumption / cost
- Error types (hallucination, convention violation, tool misuse)

## Findings

### Result: NO-GO for Ollama Cloud dispatch workers

Ollama Cloud cannot reliably sustain multi-step agent sessions on any tier. The platform hits **3 of 4 no-go criteria**:

- **No-Go #2**: Success rate 0% (0/3 trials completed). Best result was partial (73% of files edited correctly before stall).
- **No-Go #4**: Free tier exhausted mid-session (~11 min of active work). Rate limits prevented completing a single SPEC within 30 minutes. One trial consumed the entire daily/session budget, blocking the other two models from even starting.
- **No-Go (new)**: Platform reliability — 29.7% failure rate on qwen3.5 documented in March 2026. No SLA, no status page, no incident communication.

### Model intelligence: VALIDATED

The models themselves performed well when the platform allowed them to work:

- **qwen3.5:397b** read AGENTS.md, found SPEC-018, read ADR-003, and made correct edits across 16 of 22 target files (73% coverage). Lifecycle phases correctly matched the three-track model. Template defaults correctly changed to "Proposed". STORY references correctly removed. Zero hallucination, zero scope creep.
- Tool calling format works correctly for qwen3.5:397b, glm-5, and deepseek-v3.1:671b through the `/v1/chat/completions` endpoint.

### Tool calling compatibility

| Model | Tool calling | Format | Latency |
|-------|-------------|--------|---------|
| qwen3.5:397b | Works | OpenAI-standard `call_*` IDs | ~3s |
| glm-5 | Works | OpenAI-standard `call_*` IDs | ~3s |
| deepseek-v3.1:671b | Works | OpenAI-standard `call_*` IDs | ~3s |
| kimi-k2.5 | Broken | N/A — "prompt too long" on all requests | N/A |
| kimi-k2-thinking | Works | Non-standard `functions.*:N` IDs | 60-100s |

### Platform limitations

- **Opaque rate limits**: Usage measured in "GPU time" — no published token or request quotas. Free tier: ~1-2 hours of coding/day. Pro ($20/mo): 50x Free (but base unit undefined). Max ($100/mo): 250x Free.
- **Concurrency**: Free=1, Pro=3, Max=10 concurrent model slots. Running two trials simultaneously would require Pro.
- **Session/weekly resets**: Limits reset every 5 hours (session) and 7 days (weekly). At 90% usage, email notification. No graceful degradation — requests fail silently or queue indefinitely.
- **No throughput differentiation**: All tiers share the same inference pool at 42-95 tok/s. Paying more buys capacity (GPU time budget), not speed.

### Trial results

| Model | Trial | Duration | Files changed | Status | Failure mode |
|-------|-------|----------|---------------|--------|-------------|
| kimi-k2.5 | 1 | 18s | 0 | FAIL | Server-side bug — "prompt too long" on trivial prompts |
| qwen3.5:397b | 1 | ~35m (killed) | 16/22 | PARTIAL | API stall after ~11m active work; platform rate limit |
| glm-5 | 1 | <1m | 0 | FAIL | Launched after usage exhausted by qwen3.5 trial |
| deepseek-v3.1:671b | 1 | <1m | 0 | FAIL | Launched after usage exhausted by qwen3.5 trial |

### Pivot recommendation

**Pivot B (self-hosted Ollama) is most promising.** The models are smart enough — qwen3.5:397b proved it can follow swain conventions and edit artifacts correctly. The bottleneck is Ollama Cloud's rate limits, reliability, and opaque capacity. Self-hosting removes all three:

- No rate limits or session caps
- No shared inference pool — dedicated throughput
- No dependency on Ollama Cloud's availability
- Version-pinnable (avoids the qwen3.5 tool-call-printing bug in Ollama 0.17.6+)
- Cost: ~$55/month for RTX 4090 VPS, or $0 on existing hardware with a GPU

**Pivot A** (Claude SDK + Ollama inference) still requires Anthropic auth, defeating the "auth-free dispatch" goal.

**Pivot C** (abandon multi-model) remains the conservative fallback if self-hosting proves impractical.

### Research artifacts

- **Troves**: `ollama-cloud-dispatch-workers@71ed4fc` (10 sources), `ollama-cloud-subscriptions@3b14d3e` (6 sources)
- **Trial data**: `trial-kimi-k2.5-1.md`, `trial-qwen3.5-397b-1.md`, worktrees at `/tmp/spike045-*/`
- **Trial runner**: `run-trial.sh` — reusable for Pivot B testing with local Ollama

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | — | Initial creation — operator-requested spike |
