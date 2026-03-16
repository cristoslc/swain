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

## Findings: TOTP-in-the-Clear Assessment

### 1. TOTP Replay Window Mechanics

**RFC 6238 baseline:** The standard TOTP time step is 30 seconds. RFC 6238 Section 5.2 recommends validators accept "at most one time step" for network delay, giving an effective acceptance window of ~60 seconds (current step + previous step). Some implementations extend this to +/-1 step (~90 seconds). The RFC explicitly requires: "The verifier MUST NOT accept the second attempt of the OTP after the successful validation has been issued for the first OTP."

**GitHub Issue visibility timing:** Under normal conditions, a newly created GitHub Issue is visible via the REST API and triggers webhooks within milliseconds to low single-digit seconds. There is no meaningful propagation delay for API reads. RSS feeds (via tools like RSSHub, Zapier), webhook forwarding, and direct API polling all provide near-real-time notification of new issues on watched repos. During incidents, GitHub has documented webhook delays of 10-40 minutes, but normal operation is sub-second.

**Attacker timeline for replay:**

| Step | Time estimate |
|------|--------------|
| Operator creates issue with TOTP code | T+0 |
| Issue visible via API/webhooks/RSS | T+0 to T+2s |
| Attacker extracts TOTP from issue body | T+2s to T+10s (automated script) |
| Attacker creates competing issue with same TOTP | T+10s to T+20s |
| TOTP code expires (30s window, +1 step grace) | T+60s to T+90s |

An automated attacker watching the repo could replay a TOTP code within 10-20 seconds of issue creation -- well inside the 60-90 second acceptance window. The TOTP code is posted in plaintext in a public channel, so no cryptographic interception is required; it is a simple string copy from the issue body.

### 2. One-Time-Use Enforcement in a Polling Architecture

RFC 6238 requires one-time-use enforcement: once a code has been validated, the verifier must reject subsequent uses of the same code. This is the primary defense against replay within the validity window.

**The polling architecture fundamentally breaks one-time-use.**

The intake pipeline runs on a GitHub Actions cron schedule. GitHub Actions enforces a minimum cron interval of 5 minutes, with the planned default for EPIC-024 being 15 minutes. This creates a fatal timing mismatch:

| Scenario | TOTP window | Poll interval | Code age at first check |
|----------|-------------|--------------|------------------------|
| Best case | 30s | 5 min | 4.5 min expired |
| Planned default | 30s | 15 min | 14.5 min expired |
| Extended window (+/-1 step) | 90s | 15 min | 13.5 min expired |

**Implications:**

- **Expired-by-design:** By the time the poller runs, the TOTP code is always already expired. The pipeline would need to validate the code retroactively by computing what the valid TOTP was at the issue's `created_at` timestamp rather than at polling time. This transforms TOTP from a time-based challenge into a static proof-of-knowledge verified after the fact.

- **Batch replay between polls:** Multiple issues posted between polling intervals can all carry the same TOTP code (valid at the same 30-second window). The pipeline processes them in a single batch and has no way to determine which was "first." One-time-use enforcement requires a real-time verifier that consumes codes at submission time; a batch poller cannot provide this.

- **No consumed-codes ledger:** A ledger of consumed codes only prevents replay if the verifier runs within the TOTP validity window. When the verifier runs 5-15 minutes later, the ledger would need to persist across polls, but the attacker's replayed code is indistinguishable from the legitimate code -- both are the same string, both were submitted within the same TOTP window.

**Attempted mitigation -- retroactive timestamp validation:** The pipeline could compute the valid TOTP at `issue.created_at` and compare. This proves the submitter knew the shared secret at creation time. However, since the code is plaintext in the public issue body, any observer gains that same knowledge instantly. Two issues created 5 seconds apart in the same 30-second TOTP window will carry identical valid codes, and the pipeline cannot distinguish the legitimate submission from the replay.

### 3. Practical Risk Assessment

**Likelihood of active monitoring:**

| Repo profile | Monitoring likelihood | Justification |
|-------------|----------------------|--------------|
| Low-profile personal repo | Very low | Attacker must discover the repo, understand the intake system, set up monitoring, and have motivation |
| Public repo with visible CI/CD | Low | Automated scanners crawl public repos but target secrets and vulnerabilities, not work-intake injection |
| Targeted attack on known repo | High | Trivially achievable with a webhook subscription or API polling script; all tooling is off-the-shelf |

**Blast radius of successful replay:**

Per INITIATIVE-008's two-tier model, a replayed TOTP issue that passes the fast path would:

1. Skip structural/content filters (the entire point of the fast path)
2. Be classified by an agent as a SPEC, EPIC, or SPIKE
3. Have a swain artifact created following swain-design conventions
4. **The operator reviews all artifacts before any execution occurs**

The damage is bounded: the attacker can cause an unwanted artifact to be created, consuming agent compute time and polluting the artifact namespace. There is no code execution, no deployment, no data exfiltration, and no privilege escalation. The operator catches spurious artifacts during review.

However, per the Threat Model findings (above), prompt injection via a fast-tracked issue body is the amplified risk: the fast path skips content-pattern filters, so a well-crafted issue body reaching the classifying agent has a wider surface for prompt injection than one that passed the slow-path gauntlet.

**Is the risk acceptable given the two-tier model?**

The practical risk is low, but the mechanism provides **false confidence**. The TOTP code offers no meaningful security guarantee in this architecture because:

1. **Secret revealed on every use** -- The TOTP code (derived from the shared secret) is posted in plaintext. While the shared secret itself is not revealed, the code is all an attacker needs to replay.
2. **One-time-use is unenforceable** -- The polling model cannot consume codes at submission time, and batch processing cannot distinguish original from replay.
3. **Code is always stale** -- The 5-15 minute polling interval guarantees the code has expired, requiring retroactive validation that defeats TOTP's time-based security property.
4. **Any observer can replay** -- No cryptographic barrier; the code is a 6-digit string visible in the issue body.

An author allowlist (already specified for the slow path in EPIC-024) provides equivalent or better protection with zero secret exposure, since GitHub author identity cannot be spoofed without account compromise (see Threat Model, Trust Assumption #1).

### 4. GO/NO-GO Verdict

**NO-GO** -- TOTP-in-the-clear is not viable for the public intake fast path.

| Criterion | Rating | Detail |
|-----------|--------|--------|
| Replay window | FAIL | 60-90s window is exploitable in <20s by automated observers; code is plaintext |
| One-time-use | FAIL | Polling architecture (5-15 min) cannot enforce one-time-use; codes are batch-processed post-expiry |
| Retroactive validation | WEAK | Timestamp-based check proves knowledge of secret at creation time, but code is public, so all observers share that knowledge |
| Practical risk | LOW | Blast radius limited to unwanted artifact creation; operator review gate catches it |
| False confidence | HIGH | TOTP provides the appearance of authentication without substance in a polling architecture |
| Prompt injection amplification | MEDIUM | Fast path skips content filters, widening the attack surface for agent manipulation |

**Rationale:** Although the practical exploitation risk is low (limited blast radius, low-profile repos, operator review gate), TOTP-in-the-clear for a polling-based pipeline is architecturally unsound. The mechanism cannot deliver on its core promise -- proof of authorized identity -- because the proof material is public and the verification model (batch polling) cannot enforce the one-time-use property that makes TOTP secure. Adopting it would create a false sense of security that might discourage adoption of mechanisms that actually work.

**Recommended next step:** Evaluate HMAC-based signatures over the issue body (Question 2a from this spike's research questions). In an HMAC scheme, the shared secret is never revealed in the issue -- only a signature derived from the secret and the issue content is posted. The signature can be verified retroactively at polling time and cannot be replayed for a different issue body, making it naturally resistant to both the replay and batch-verification problems that disqualify TOTP.

**Sources consulted:**
- RFC 6238 (TOTP), Sections 4.1, 5.2, 6 -- https://datatracker.ietf.org/doc/html/rfc6238
- GitHub REST API rate limits -- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- GitHub webhook troubleshooting -- https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks
- GitHub Actions scheduled workflow constraints -- https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions
- GitHub Actions minimum cron frequency changelog -- https://github.blog/changelog/2019-11-01-github-actions-scheduled-jobs-maximum-frequency-is-changing/
- "Time Is on My Side: Forward-Replay Attacks to TOTP Authentication" (SocialSec 2023) -- https://link.springer.com/chapter/10.1007/978-981-99-5177-2_7
