---
title: "Docker Sandboxes OAuth Limitation Workaround"
artifact: SPIKE-032
track: container
status: Complete
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-011
parent-vision: VISION-002
question: "What workarounds exist for docker/desktop-feedback#198 (OAuth/Max subscription broken in Docker Sandboxes MITM proxy), and which provides the best path for unattended Claude Code operation?"
gate: Pre-MVP
risks-addressed:
  - Docker Sandboxes (strongest isolation) unusable for subscription users
  - Forced fallback to weaker native sandboxing for unattended use
evidence-pool: |
  - docker/desktop-feedback#198 (Open, 2026-03-15): MITM proxy breaks api.claude.ai connectivity
  - docker/for-mac#7842 (Open, 2026-01-30): apiKeyHelper injection bug, fixed in DD 4.60.1
  - Claude Code auth docs: https://code.claude.com/docs/en/authentication
  - Docker Sandboxes network policy docs: https://docs.docker.com/ai/sandboxes/network-policies/
  - Docker Sandboxes Claude Code docs: https://docs.docker.com/ai/sandboxes/agents/claude-code/
  - anthropics/claude-code#34785: OAuth token refresh uses api.anthropic.com endpoints
  - anthropics/claude-code#1736: Docker container credential persistence patterns
linked-artifacts:
  - SPEC-067
  - SPEC-049
depends-on-artifacts: []
---

# Docker Sandboxes OAuth Limitation Workaround

## Summary

**Verdict: Conditional Go.** Docker Sandboxes work for unattended Claude Code when using `ANTHROPIC_API_KEY` (API billing). OAuth/Max subscription authentication is fundamentally broken by the MITM proxy's inability to tunnel `api.claude.ai` traffic, and no upstream fix has shipped as of Docker Desktop 4.64. A separate `apiKeyHelper` injection bug (docker/for-mac#7842) was fixed in Docker Desktop 4.60.1 but is orthogonal to the core MITM issue. The recommended path for swain is: support API key auth as the primary Docker Sandboxes credential path, document the OAuth limitation clearly, and monitor the upstream issue for resolution.

## Question

What workarounds exist for docker/desktop-feedback#198 (OAuth/Max subscription broken in Docker Sandboxes MITM proxy), and which provides the best path for unattended Claude Code operation?

## Go / No-Go Criteria

- **Go (workaround exists):** A documented method allows Claude Code with Max/OAuth authentication to operate inside Docker Sandboxes — either by bypassing the MITM proxy for OAuth flows, using API key auth as a fallback, or via an upstream fix in Docker Desktop.
- **No-Go (no workaround):** The MITM proxy fundamentally cannot handle OAuth token refresh, and there is no timeline for an upstream fix. API key fallback is not viable for the operator's subscription type.
- **Threshold:** The workaround must not require baking credentials into the Docker image or persisting tokens inside the sandbox filesystem.

## Pivot Recommendation

If no workaround exists: document Docker Sandboxes as API-key-only for unattended use. Operators with Max/OAuth subscriptions use native sandbox (Tier 1) for unattended work until Docker fixes the issue. Track the upstream issue and re-evaluate when Docker Desktop ships a fix.

## Findings

### 1. Upstream issue status (docker/desktop-feedback#198)

**Status: Open, no fix shipped, no timeline.**

The issue was filed 2026-03-15 against Docker Desktop 4.64.0 (sandbox plugin v0.12.0). It has zero comments and labels `area/sandbox`, `kind/bug`, `platform/windows`. The reporter's debugging is thorough and demonstrates three failure modes:

| Mode | Result |
|------|--------|
| MITM (default) | Proxy re-signs TLS with its own CA. `api.claude.ai` drops the connection (empty reply). |
| Bypass (`--bypass-host api.claude.ai`) | Proxy attempts CONNECT tunnel, returns 502 Bad Gateway. |
| No proxy (`unset HTTPS_PROXY`) | DNS cannot resolve (sandbox DNS depends on the proxy). |

Crucially, `api.anthropic.com` works fine in all modes — the MITM proxy successfully intercepts and re-signs traffic to that domain. Only `api.claude.ai` is affected, likely because it enforces stricter TLS policies (certificate pinning or SNI validation) that reject the forged certificate.

### 2. Two distinct bugs, often conflated

There are **two separate issues** affecting OAuth in Docker Sandboxes:

| Bug | Mechanism | Fixed? | Affects swain? |
|-----|-----------|--------|----------------|
| **docker/for-mac#7842**: `apiKeyHelper` injection | Sandbox plugin writes `apiKeyHelper: "echo proxy-managed"` into `~/.claude/settings.json`, overriding OAuth credentials with a literal string. | **Yes** — fixed in Docker Desktop 4.60.1. swain-box already cleans this up as a belt-and-suspenders measure. | Only on old Docker Desktop versions. |
| **docker/desktop-feedback#198**: MITM proxy vs `api.claude.ai` | The proxy cannot tunnel traffic to `api.claude.ai` — neither MITM mode nor bypass mode works. | **No** — open, no comments from Docker team, no timeline. | Yes — this is the fundamental blocker. |

### 3. Claude Code authentication architecture

Claude Code supports multiple auth methods with this precedence (highest first):

1. Cloud provider env vars (`CLAUDE_CODE_USE_BEDROCK`, etc.)
2. `ANTHROPIC_AUTH_TOKEN` env var (bearer token for LLM gateways)
3. `ANTHROPIC_API_KEY` env var (API key, sent as `X-Api-Key` header)
4. `apiKeyHelper` script output (dynamic/rotating credentials)
5. Subscription OAuth credentials from `/login` (default for Pro/Max/Teams/Enterprise)

**Key routing difference:**
- **API key auth** (`ANTHROPIC_API_KEY`): requests go to `api.anthropic.com` with `X-Api-Key` header. This works through the Docker Sandboxes MITM proxy.
- **OAuth/subscription auth**: OAuth token refresh endpoints are on `api.anthropic.com` (e.g., `/api/oauth/claude_cli/client_data`, `/api/oauth/profile`), but subscription inference calls route through `api.claude.ai`. The MITM proxy breaks `api.claude.ai` connectivity, so even with a valid OAuth token, the actual Claude API calls fail.

### 4. Workaround analysis

#### 4a. ANTHROPIC_API_KEY fallback (VIABLE — current approach)

**How it works:** Set `ANTHROPIC_API_KEY` in the host shell profile (`~/.zshrc`). Docker Desktop's daemon reads env vars from the profile at startup. The sandbox plugin detects the key and injects it via the MITM proxy into requests to `api.anthropic.com`.

**Pros:**
- Works today, no upstream fix needed
- No credentials baked into Docker image
- Proxy manages injection (credentials never enter the VM filesystem)
- swain-box already implements this path with detection and warning

**Cons:**
- Requires separate API billing (pay-per-token, not flat-rate subscription)
- Operators with only a Max/Pro subscription and no API credits cannot use Docker Sandboxes
- Two billing paths creates operator confusion

**Meets threshold:** Yes — credentials are proxy-managed, never persisted in sandbox.

#### 4b. CLAUDE_CODE_OAUTH_TOKEN env var (NOT VIABLE for Docker Sandboxes)

**How it works:** Claude Code reads a JSON blob from the `CLAUDE_CODE_OAUTH_TOKEN` environment variable containing `accessToken`, `refreshToken`, and `expiresAt`. This takes precedence over the credentials file.

**Why it fails in Docker Sandboxes:** Even if the token could be passed into the sandbox environment, the inference calls still need to reach `api.claude.ai`, which the MITM proxy blocks. The token itself is valid, but the network path is broken. This is the same root cause as the standard OAuth flow — the problem is not token acquisition, it is that `api.claude.ai` rejects MITM'd TLS connections.

**Meets threshold:** N/A — does not work.

#### 4c. Proxy bypass for api.claude.ai (NOT VIABLE)

**How it works:** `docker sandbox network proxy <name> --bypass-host api.claude.ai` tells the proxy to use a CONNECT tunnel instead of MITM interception.

**Why it fails:** The issue reporter tested this explicitly. Bypass mode returns 502 Bad Gateway for `api.claude.ai`. The sandbox proxy implementation appears to have a bug in its CONNECT tunnel for this specific host. DNS resolution also depends on the proxy, so unsetting the proxy entirely breaks name resolution.

**Meets threshold:** N/A — does not work.

#### 4d. Custom Docker image (DEFERRED — separate track)

**How it works:** Build a custom Docker image with Claude Code pre-installed, pass `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` as `-e` env vars at `docker run` time. This bypasses Docker Sandboxes entirely (no MITM proxy) but also loses the proxy's credential injection and network policy enforcement.

**Relevance:** This is the Tier 2b (container-level) isolation path from VISION-002. It is a viable alternative to Docker Sandboxes but operates at a different isolation level. Not a workaround for the MITM bug — it sidesteps it.

#### 4e. Wait for upstream fix (MONITOR)

Docker has not commented on desktop-feedback#198 or indicated a timeline. The related apiKeyHelper bug (for-mac#7842) was fixed within ~2 weeks in Docker Desktop 4.60.1, suggesting Docker does respond to sandbox-related issues. However, the MITM proxy issue is architecturally more complex — it may require changes to the proxy's CONNECT tunnel implementation or adding `api.claude.ai` to a built-in bypass list.

### 5. swain-box current state

The existing `swain-box` script (at `skills/swain/scripts/swain-box`) already handles the OAuth limitation correctly:

- Detects whether `ANTHROPIC_API_KEY` is available (in env or shell profile)
- Warns clearly when no API key is found, explaining the MITM limitation
- Points operators to the Tier 1 native launcher (`scripts/claude-sandbox`) as the alternative for Max/Pro users
- Cleans up stale `apiKeyHelper` injection from the for-mac#7842 bug
- Requires Docker Desktop 4.58+ (verified via `docker sandbox --help`)

No changes are needed to swain-box for the current situation. The script's behavior is already aligned with the findings of this spike.

### 6. Docker Desktop version timeline

| Version | Date | Sandbox relevance |
|---------|------|-------------------|
| 4.58.0 | ~Jan 2026 | `docker sandbox` subcommand introduced |
| 4.58.1 | ~Jan 2026 | apiKeyHelper injection bug introduced (for-mac#7842) |
| 4.59.0 | ~Feb 2026 | Sandbox plugin v0.10.1 |
| 4.60.1 | ~Feb 2026 | apiKeyHelper injection bug fixed (confirmed by reporter) |
| 4.61.0 | ~Feb 2026 | Sandbox plugin v0.12.0 |
| 4.64.0 | ~Mar 2026 | MITM proxy vs api.claude.ai still broken (desktop-feedback#198) |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Created for INITIATIVE-011 decomposition |
| Complete | 2026-03-19 | — | Conditional Go — API key auth works; OAuth broken by MITM, no upstream fix timeline |
