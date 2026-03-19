---
title: "swain-box: OpenAI Codex Runtime Support"
artifact: SPEC-070
track: implementable
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: feature
parent-epic: EPIC-030
parent-initiative: ""
linked-artifacts:
  - SPEC-068
depends-on-artifacts:
  - SPEC-068
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-box: OpenAI Codex Runtime Support

## Problem Statement

OpenAI's Codex CLI (`codex`) uses Docker-based sandboxing natively and may surface as a Docker Sandboxes runtime. When detected, swain-box must handle OPENAI_API_KEY passthrough cleanly and verify that Codex's sandbox is isolated from Claude and Copilot sandboxes.

## External Behavior

### Codex detection

Runtime name: `codex`. Detected via the standard probe in SPEC-068:
```sh
docker sandbox run codex --version >/dev/null 2>&1
```

### Credential passthrough

When `codex` is selected as the runtime, swain-box applies Codex-specific credential logic:

1. If `OPENAI_API_KEY` is set, pass it through the credential proxy (no `-e` flags).
2. If not set, warn to stderr: "swain-box: NOTE: OPENAI_API_KEY not set. OpenAI Codex may require authentication inside the sandbox."
3. Unset ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, and GITHUB_TOKEN before launch.

### Isolation verification

A `test-swain-box-codex-isolation.sh` script verifies:
- Codex sandbox cannot read files from Claude or Copilot sandbox namespaces
- ANTHROPIC_API_KEY and GITHUB_TOKEN are absent inside the Codex sandbox
- OPENAI_API_KEY is present inside the Codex sandbox (when set on host)

## Acceptance Criteria

**AC-1: Codex detected when available**
- Given `docker sandbox run codex --version` exits 0
- When swain-box probes runtimes
- Then `codex` appears in the selection menu

**AC-2: OPENAI_API_KEY forwarded**
- Given OPENAI_API_KEY is set on the host
- When codex runtime is selected
- Then Docker Sandboxes receives the key via its credential proxy

**AC-3: Graceful warning when no key**
- Given OPENAI_API_KEY is not set
- When codex runtime is selected
- Then a warning is printed to stderr and launch proceeds

**AC-4: Competing credentials unset**
- Given ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, and GITHUB_TOKEN are set on host
- When codex runtime is selected
- Then all three are unset before `docker sandbox run codex` executes

**AC-5: Isolation verified**
- Given claude and codex sandboxes exist
- When isolation tests run
- Then neither sandbox can access the other's filesystem or environment credentials

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 through AC-5 | test-swain-box-codex-isolation.sh | — |

## Scope & Constraints

**In scope:** Codex credential passthrough, credential cleanup for competing runtimes, isolation test suite.
**Out of scope:** Codex model selection or configuration inside the sandbox.

**Constraints:**
- Depends on Docker Sandboxes exposing a `codex` runtime image (forward-compatible spec)
- OPENAI_API_KEY is the only credential mechanism — no OAuth fallback for Codex (as of 2026-03)

## Implementation Approach

TDD cycles:
1. Test OPENAI_API_KEY passthrough (mock sandbox)
2. Test that ANTHROPIC_API_KEY and GITHUB_TOKEN are unset when codex is selected
3. Manual isolation test (requires Docker Sandboxes with codex image)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Initial creation; Codex auth passthrough and isolation for EPIC-030 |
| Complete | 2026-03-19 | — | Codex credential passthrough implemented in swain-box |
