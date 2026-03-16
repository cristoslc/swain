---
title: "Authentication for Public Intake Channels"
artifact: SPIKE-025
track: research
status: Proposed
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
parent-initiative: INITIATIVE-008
linked-artifacts:
  - INITIATIVE-008
  - EPIC-024
---

# Authentication for Public Intake Channels

## Research Question

What authentication mechanism should swain use to fast-track work intake from public channels (e.g., GitHub Issues on public repos) where all content is visible in the clear?

## Context

INITIATIVE-008 defines a two-tier intake model: authenticated issues skip structural/content filters and are fast-tracked to agent processing. The auth mechanism must work on public repos where issue content is visible to anyone.

TOTP (time-based one-time password) was the initial candidate, but TOTP codes posted in public issues are visible to all observers, creating a potential replay window.

## Questions to Answer

1. **TOTP replay risk:** Can TOTP codes in public issues be replayed within the validity window (typically 30s)? What is the practical attack surface — an attacker would need to see the issue, extract the code, and submit a competing issue before the window expires.
2. **Alternative auth primitives:**
   - HMAC signatures over issue body (proves authorship without revealing secret)
   - GitHub App-signed payloads (leverages GitHub's own trust model)
   - Commit-signed references (tie issue to a signed commit)
   - Asymmetric challenge-response (pre-shared public key, sign the issue body)
   - GitHub's built-in author verification (is author allowlist sufficient for the fast path?)
3. **Threat model:** Who are we defending against? Random drive-by issue creation? Targeted spoofing by someone watching the repo? Automated bots?
4. **Usability:** How much friction does each mechanism add to the operator's workflow when submitting an issue?

## Constraints

- Must work for public repos
- Must not require the submitter to have repo admin access
- Should be operator-friendly (not require complex tooling to submit an issue)
- The filter pipeline is deterministic — auth validation must be computable without LLM

## Expected Output

- GO/NO-GO on TOTP-in-the-clear for public repos
- Recommended auth mechanism with rationale
- Threat model summary for the chosen mechanism
- Integration sketch showing how the auth check fits into the filter chain

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-16 | — | Created during INITIATIVE-008 brainstorming |

## Findings: Threat Model

### Threat Actors

| Actor | Motivation | Capability |
|-------|-----------|------------|
| **Drive-by spammer** | Low; opportunistic mischief, SEO spam, or testing bots | Can create a GitHub account and file issues; no repo-specific knowledge; low persistence |
| **Targeted attacker** | Medium–High; inject malicious work items (e.g., "add backdoor to auth module") to influence what the agent builds | Watches the repo, understands the intake format, can craft well-formed issues that pass structural filters |
| **TOTP replayer** | Medium; bypass auth to fast-track a crafted issue | Monitors public issues in real-time, can extract a TOTP code and submit a competing issue within the validity window |
| **Bot operator** | Medium; overwhelm the intake pipeline to cause denial-of-service or drown legitimate issues in noise | Automated scripts, multiple GitHub accounts, API-level issue creation at up to 80 content-generating requests/minute per account |
| **Prompt injector** | Medium–High; manipulate the classifying agent into misrouting, escalating, or executing unintended actions | Crafts issue body content designed to override agent instructions; no special access required beyond issue creation |

### Attack Vectors

| Vector | Likelihood | Impact | Existing Mitigation (Slow Path) |
|--------|-----------|--------|-------------------------------|
| **Drive-by spam** | High — public repos accept issues from any GitHub account by default | Low — slow-path filters (label filter, author allowlist, content pattern matching) reject unstructured or unrecognized input before agent processing begins | **Fully mitigated by slow path.** Label filter requires triage+ permission (see Trust Assumptions); author allowlist rejects unknown submitters; content patterns reject garbage. |
| **Targeted spoofing** | Medium — requires repo observation and format knowledge, but all issue templates and past issues are public | High — a well-crafted issue that passes slow-path filters could inject a malicious work item into the agent's task queue | **Partially mitigated.** Author allowlist blocks unknown authors. Content pattern matching catches obvious anomalies. However, a sufficiently well-crafted issue from an allowlisted author's compromised account would pass all filters. |
| **TOTP replay** | Low–Medium — attacker must (1) monitor the repo in real-time, (2) extract the code, (3) craft a plausible issue, and (4) submit it within the TOTP validity window | High — replayed TOTP grants fast-path access, bypassing all slow-path filters entirely | **Not mitigated.** TOTP codes in public issues are visible in the clear. The validity window per RFC 6238 is 30 seconds nominal, but implementations commonly accept one adjacent window, extending the effective window to 60–90 seconds. This is exploitable by a motivated attacker with automation. |
| **Bot automation / flooding** | Medium — requires multiple accounts or tokens but is straightforward to automate | Medium — could overwhelm the intake pipeline, causing delays or resource exhaustion for the classifying agent | **Partially mitigated.** GitHub's secondary rate limits cap content-generating requests at 80/minute and 500/hour per authenticated user. Slow-path filters reject most bot-generated issues. However, a botnet using multiple accounts could bypass per-account rate limits. |
| **Prompt injection via issue body** | Medium — requires knowledge of the classifying agent's behavior, but LLM prompt injection is a well-documented attack surface | High — successful injection could cause the agent to misclassify, escalate, or execute unintended actions; effect depends on the agent's permission scope | **Partially mitigated.** The filter pipeline is deterministic (no LLM), so injection cannot affect the filter stage. However, issues that pass filters reach the classifying agent, where injection becomes relevant. The fast path (auth bypass) amplifies this risk by skipping filters entirely. |

### Trust Assumptions

**1. GitHub author identity is reliable for allowlist purposes.**

GitHub usernames are globally unique and tied to authenticated accounts. Every issue creation event on the GitHub API is attributed to the authenticated user — there is no mechanism to spoof the `author` field on an issue. An attacker cannot impersonate a GitHub username without compromising that account's credentials. However, account compromise (phished tokens, leaked PATs) would allow impersonation. The allowlist trusts GitHub's authentication, not the person.

*Evidence:* GitHub requires authentication for all write operations. The REST API attributes the `user` field of an issue to the OAuth/PAT-authenticated identity. Username changes are possible but produce a different username — the old one becomes available for re-registration, which is a known (but low-probability) vector.

**2. GitHub rate limits provide baseline flood protection, but are not sufficient as a sole defense.**

GitHub enforces both primary and secondary rate limits on content-creating endpoints:
- Primary: 5,000 requests/hour per authenticated user (15,000 for GitHub Enterprise Cloud).
- Secondary: no more than 80 content-generating requests/minute and 500/hour per authenticated user.
- Unauthenticated: 60 requests/hour per IP address.

These limits apply per-account. A determined attacker with multiple accounts can multiply throughput linearly. GitHub also applies undisclosed abuse-detection heuristics that may throttle or block suspicious patterns.

*Evidence:* GitHub REST API rate limit documentation (docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). Secondary limits return HTTP 403 or 429 with retry headers.

**3. The TOTP validity window is exploitable on public channels.**

RFC 6238 defines a default 30-second time step. Section 5.2 recommends accepting "at most one time step" for network delay tolerance, extending the effective window to 60 seconds. Some implementations accept two backward steps, yielding up to 89 seconds of validity (RFC 6238, Section 6). On a public repo, an attacker can observe the TOTP code immediately upon issue creation (via API polling, webhook, or RSS), giving them the full remaining window to craft and submit a competing issue. Automated tooling could complete this in under 5 seconds.

*Evidence:* RFC 6238, Sections 4.1, 5.2, and 6. Public GitHub issues are available via the REST API and real-time via webhooks, with no delay between creation and visibility.

**4. Label permissions restrict fast-path abuse surface.**

Only users with triage access or higher can apply labels to issues on a repository. On a public repo, random users (read-only access) cannot add labels. This means a label-based auth scheme (e.g., "apply `swain:authenticated` label to fast-track") is naturally restricted to collaborators. However, if the fast-path trigger is content-based (e.g., a TOTP code in the issue body) rather than label-based, this protection does not apply.

*Evidence:* GitHub repository roles documentation — triage role is the minimum for applying/dismissing labels; read-only users cannot apply labels (docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization). Additionally, repo owners can enable interaction limits (collaborators-only, prior-contributors-only, or existing-users-only) for 24 hours to 6 months, providing a temporary throttle on who can create issues at all.
