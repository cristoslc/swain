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

If No-Go on free tier (confirmed — see Findings):

- **Pivot A**: Ollama Cloud paid tier (Pro $20/mo or Max $100/mo). Same setup already built and tested — just pay for capacity. Pro gives 3 concurrent sessions and 50x the free budget; Max gives 10 concurrent and 250x. The qwen3.5 trial stall may have been purely a free-tier budget issue. **Test first**: re-run qwen3.5 trial on Pro to determine if paid tier sustains a full session. Cost: $20-100/month.
- **Pivot B**: DeepSeek API direct ($0.27/M tokens). Cheapest per-session (~$0.01-0.03/SPEC). 671B deepseek-v3.1 with tool calling confirmed working. Needs an agent framework (no OpenCode equivalent), and adds another API key dependency. Auth-free in the 1Password sense but not zero-auth.
- **Pivot C**: Self-host Ollama with a 32B model (qwen2.5-coder:32b) on a single-GPU VPS (~$55/month). Removes rate limits and cloud dependency. But 32B models are a fundamentally different capability tier — untested for swain convention compliance. **671B self-hosting is not viable**: requires 5-8x H100 GPUs at $3,900-17,500/month (see `self-hosted-llm-inference-costs` trove).
- **Pivot D**: Claude Code Agent SDK + Ollama inference. Still needs Anthropic auth — defeats the auth-free dispatch goal.
- **Pivot E**: Abandon multi-model dispatch; keep all agent work on Claude Code and focus on reducing per-session cost through model routing (SPIKE-026).

## Test Protocol

### Setup
1. Create an Ollama Cloud account and API key
2. Install OpenCode CLI
3. Configure OpenCode to use `https://ollama.com/v1` as base URL with the API key
4. Select a completed mechanical SPEC as the test case — SPEC-018 (Update Artifact Definitions and Templates), 22 files, 6 ACs

### Trial Runs (5x per model)
1. Start OpenCode in the swain repo root via `run-trial.sh <model> <trial-number>`
2. Prompt: "Read AGENTS.md, then implement SPEC-018 following swain conventions"
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

### Result: NO-GO for Ollama Cloud free-tier dispatch workers

Ollama Cloud free tier cannot sustain multi-step agent sessions. The platform hits **3 of 4 no-go criteria**:

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
| qwen3.5:397b | 1 | ~35m (killed) | 16/22 | PARTIAL | API stall after ~11m active work; free-tier budget exhausted |
| glm-5 | 1 | <1m | 0 | FAIL | Launched after usage exhausted by qwen3.5 trial |
| deepseek-v3.1:671b | 1 | <1m | 0 | FAIL | Launched after usage exhausted by qwen3.5 trial |

### Next steps

1. Re-run glm-5 and deepseek-v3.1 trials after Ollama session reset (pending)
2. Consider upgrading to Pro ($20/mo) and re-running qwen3.5 to test Pivot A
3. Update pivot section with corrected self-hosting costs (done — see `self-hosted-llm-inference-costs` trove)

### Research artifacts

- **Troves**: `ollama-cloud-dispatch-workers@71ed4fc` (10 sources), `ollama-cloud-subscriptions@3b14d3e` (6 sources), `self-hosted-llm-inference-costs` (6 sources)
- **Trial data**: `trial-kimi-k2.5-1.md`, `trial-qwen3.5-397b-1.md`, worktrees at `/tmp/spike045-*/`
- **Trial runner**: `run-trial.sh` — reusable for retry and Pivot A testing

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | — | Initial creation — operator-requested spike |
