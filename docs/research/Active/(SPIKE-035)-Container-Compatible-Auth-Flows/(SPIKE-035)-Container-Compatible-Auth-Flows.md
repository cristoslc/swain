---
title: "Container-Compatible Auth Flows Per Runtime"
artifact: SPIKE-035
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-013
parent-vision: VISION-002
question: "Which agent runtimes support device-code or non-browser OAuth flows suitable for containers, and what are the exact commands?"
gate: Pre-MVP
risks-addressed:
  - Browser-based OAuth cannot complete inside containers (localhost callback unreachable)
  - swain-box _login_cmd table may have commands that silently fail in sandboxed environments
evidence-pool: ""
linked-artifacts:
  - SPEC-092
  - SPEC-093
  - SPIKE-032
  - SPIKE-034
depends-on-artifacts: []
---

# Container-Compatible Auth Flows Per Runtime

## Summary

Several agent runtimes use browser-based OAuth that cannot complete inside containers or microVMs because the browser callback to localhost is unreachable from inside the sandbox. This spike documents which runtimes have container-compatible auth alternatives and what the exact commands are.

## Question

Which agent runtimes support device-code or non-browser OAuth flows suitable for containers, and what are the exact commands?

## Go / No-Go Criteria

- **Go:** Each supported runtime has a documented, tested container-compatible auth flow (device code, token paste, API key, or confirmed working browser flow).
- **No-Go:** One or more runtimes have no workable container auth path, requiring upstream feature requests or exclusion from swain-box.
- **Threshold:** All six runtimes (claude, codex, copilot, gemini, kiro, opencode) must have a documented auth path or a documented "no path exists" finding.

## Pivot Recommendation

If a runtime has no container-compatible auth flow: document it as unsupported for subscription auth in swain-box and default to API key auth for that runtime, or exclude it from the container isolation option.

## Findings

### Known results

| Runtime | Default login | Works in container? | Container-compatible alternative | Status |
|---------|--------------|--------------------|---------------------------------|--------|
| claude | `/login` | Yes | OAuth flow completes — container reaches `api.claude.ai` directly | Confirmed |
| codex | `codex login` | No (browser callback fails) | `codex login --device-auth` (device code flow) | Confirmed |
| copilot | `/login` | Likely yes (device code flow) | Uses GitHub device code flow by default | Unverified |
| gemini | (login prompt on first run) | Unknown | Unknown | Needs research |
| kiro | `kiro-cli login` | Unknown | Unknown | Needs research |
| opencode | `/connect` | Unknown | Unknown | Needs research |

### Research needed

- **copilot:** Verify that `/login` inside a container actually completes the device code flow. Test in a `docker/sandbox-templates:copilot` container (if available) or a generic container with GitHub Copilot CLI installed.
- **gemini:** Determine the exact auth mechanism. Does it use browser OAuth? Is there a `--device-auth` equivalent or API key env var?
- **kiro:** Determine if `kiro-cli login` uses browser OAuth. Check for device code or token-paste alternatives.
- **opencode:** Determine what `/connect` does. Is it browser-based? Is there a token or API key alternative?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation with known findings for claude and codex |
