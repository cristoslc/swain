---
source-id: omo-slim-council
title: oh-my-opencode-slim — Council Agent Guide
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/council.md
fetched: 2026-05-05
type: documentation
---

# Council Agent Guide

Multi-model consensus engine for cases where you want more than one model's judgment.

## Architecture

Two separate model layers:

1. **Council agent model** — Configured like any other agent. Does final synthesis. Set via preset's `council` entry or `agents.council` override.
2. **Councillor models** — Fan-out models running in parallel. Configured under `council.presets.<preset>.<councillor>.model`.

```
User / Orchestrator
        |
        v
Council agent (@council, your synthesizer model)
        |
        +--> Councillor A (preset model)
        +--> Councillor B (preset model)
        +--> Councillor C (preset model)
        |
        v
Council agent synthesizes councillor results → Final answer
```

## Quick Setup

```jsonc
{
  "preset": "openai",
  "presets": {
    "openai": {
      "council": { "model": "openai/gpt-5.5" }
    }
  },
  "council": {
    "presets": {
      "default": {
        "alpha": { "model": "openai/gpt-5.4-mini" },
        "beta": { "model": "google/gemini-3-pro" },
        "gamma": { "model": "openai/gpt-5.3-codex" }
      }
    }
  }
}
```

## Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `council.presets` | object | — | Required. Named councillor presets |
| `council.default_preset` | string | `"default"` | Preset when none specified |
| `council.timeout` | number | `180000` | Per-councillor timeout (ms) |
| `council.councillor_execution_mode` | string | `"parallel"` | `parallel` or `serial` |
| `council.councillor_retries` | number | `3` | Retries on empty provider response |

## Councillor Role Prompts

Each councillor can receive a steering prompt:

```jsonc
"review-board": {
  "reviewer": {
    "model": "openai/gpt-5.4-mini",
    "prompt": "Focus on bugs, edge cases, and failure modes."
  },
  "architect": {
    "model": "google/gemini-3-pro",
    "prompt": "Focus on maintainability, boundaries, and long-term design."
  }
}
```

## Usage

```text
@council Should we use a job queue or an outbox pattern here?
```

Orchestrator delegates sparingly (council is most expensive path).

## Output Format

1. `Council Response` — synthesized final answer
2. `Councillor Details` — each councillor's individual response
3. `Council Summary` — agreement, disagreement, uncertainty; confidence: `unanimous`, `majority`, or `split`
4. Footer: `Council: 2/3 councillors responded (alpha: gpt-5.4-mini, beta: gemini-3-pro)`

## Failure Handling

| Scenario | Behavior |
|----------|----------|
| Some councillors fail | Synthesize from successful ones |
| All councillors fail | Return error |
| Preset has zero councillors | Return error |
| Empty provider responses | Retry up to `councillor_retries` times |
| Timeout | Mark councillor `timed_out`; synthesize from rest |

## Serial Mode

Use for single-model setups where parallel launches contend for the same provider/session limits:

```jsonc
"council": {
  "councillor_execution_mode": "serial",
  "presets": {
    "default": {
      "alpha": { "model": "openai/gpt-5.4-mini" },
      "beta": { "model": "openai/gpt-5.4-mini" }
    }
  }
}
```
