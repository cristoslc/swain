---
title: "swain-box: GitHub Copilot Runtime Support"
artifact: SPEC-069
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

# swain-box: GitHub Copilot Runtime Support

## Problem Statement

GitHub Copilot's CLI agent (`gh copilot` or the VS Code agent backend) may support Docker Sandboxes as a runtime surface. When it does, swain-box needs to handle Copilot-specific auth (GITHUB_TOKEN or `gh auth` credential file) without baking tokens into sandbox state, and verify that Copilot's sandbox is isolated from the Claude sandbox.

## External Behavior

### Copilot detection

Runtime name: `copilot`. Detected via the standard probe in SPEC-068:
```sh
docker sandbox run copilot --version >/dev/null 2>&1
```

### Credential passthrough

When `copilot` is selected as the runtime, swain-box applies Copilot-specific credential logic before the `exec`:

1. If `GITHUB_TOKEN` is set in the host environment, pass it through (Docker Sandboxes credential proxy handles injection — no `-e` flags needed).
2. If `GITHUB_TOKEN` is not set, check for `gh auth token` output:
   ```sh
   _gh_token=$(gh auth token 2>/dev/null || true)
   ```
   If non-empty, export as `GITHUB_TOKEN`.
3. If neither is available, warn to stderr: "swain-box: NOTE: GITHUB_TOKEN not set. GitHub Copilot may require authentication inside the sandbox."
4. Unset any ANTHROPIC_API_KEY and CLAUDE_CODE_OAUTH_TOKEN before launch (prevent credential cross-contamination between runtimes).

### Isolation verification

A `test-swain-box-copilot-isolation.sh` script verifies:
- Copilot sandbox cannot read files from the Claude sandbox's filesystem namespace
- ANTHROPIC_API_KEY is absent inside the Copilot sandbox environment
- GITHUB_TOKEN is present inside the Copilot sandbox (when set on host)

## Acceptance Criteria

**AC-1: Copilot detected when available**
- Given `docker sandbox run copilot --version` exits 0
- When swain-box probes runtimes
- Then `copilot` appears in the selection menu

**AC-2: GITHUB_TOKEN forwarded from environment**
- Given GITHUB_TOKEN is set on the host
- When copilot runtime is selected
- Then Docker Sandboxes receives the token via its credential proxy

**AC-3: gh auth token fallback**
- Given GITHUB_TOKEN is not set but `gh auth token` returns a token
- When copilot runtime is selected
- Then that token is exported as GITHUB_TOKEN before launch

**AC-4: Graceful warning when no token**
- Given neither GITHUB_TOKEN nor `gh auth token` yield a value
- When copilot runtime is selected
- Then a clear warning is printed to stderr and launch proceeds (not blocked)

**AC-5: Claude credentials unset for Copilot launch**
- Given ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN are set on the host
- When copilot runtime is selected
- Then both are unset before `docker sandbox run copilot` executes

**AC-6: Isolation verified**
- Given both claude and copilot sandboxes exist
- When isolation tests run
- Then each sandbox cannot access the other's filesystem or environment credentials

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 through AC-6 | test-swain-box-copilot-isolation.sh | — |

## Scope & Constraints

**In scope:** Copilot credential passthrough, Claude credential cleanup, isolation test suite.
**Out of scope:** Copilot feature configuration (which repos, models, etc.) — that is the operator's concern inside the sandbox. Also out of scope: VS Code extension integration.

**Constraints:**
- Depends on Docker Sandboxes exposing a `copilot` runtime image (may be aspirational at time of writing — spec is forward-compatible)
- `gh` CLI is a soft dependency: if absent, fall back to GITHUB_TOKEN env var only

## Implementation Approach

TDD cycles:
1. Test GITHUB_TOKEN passthrough (mock sandbox, verify env var present in exec args)
2. Test `gh auth token` fallback (mock `gh` binary)
3. Test that ANTHROPIC_API_KEY is unset when copilot is selected
4. Manual isolation test (requires Docker Sandboxes with copilot image)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Initial creation; Copilot auth passthrough and isolation for EPIC-030 |
| Complete | 2026-03-19 | — | Copilot credential passthrough implemented in swain-box |
