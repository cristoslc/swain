---
title: "Authentication for Public Intake Channels"
artifact: SPIKE-025
track: research
status: Complete
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
| Complete | 2026-03-16 | — | TOTP NO-GO; HMAC-SHA256 recommended with author-allowlist warm path |

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

## Findings: Alternative Auth Mechanisms

### 1. HMAC Signatures Over Issue Body

**How it works:** The operator computes `HMAC-SHA256(shared_secret, canonical_issue_body)` and appends the resulting hex digest to the issue -- typically as a footer line like `<!-- swain-auth: hmac-sha256:a1b2c3d4... -->`. The filter chain strips the signature line, recomputes the HMAC over the remaining body, and compares.

**Canonicalization matters.** GitHub normalizes markdown on submission (trailing whitespace, line endings, HTML entity encoding). The HMAC must be computed over the *post-normalization* form, or the operator must use a CLI tool that predicts the normalization. In practice this means the signing tool should either (a) submit via GitHub API and sign the API-returned body, or (b) enforce a strict canonical form (UTF-8, LF line endings, no trailing whitespace, no HTML entities).

**Security properties:**
- **Replay-proof:** Yes -- the signature is bound to the exact issue body. Replaying the signature with a different body fails.
- **Content-bound:** Yes -- any modification to the body invalidates the signature.
- **Secret exposure risk:** An attacker who observes multiple (body, signature) pairs cannot recover the secret in polynomial time, assuming HMAC-SHA256. The security reduction to the underlying hash function means the attacker would need to find collisions in SHA-256 or break the HMAC construction itself. With a 256-bit secret, brute force is infeasible. However, if the secret has low entropy (e.g., a short passphrase), offline brute force is possible since the attacker has oracle pairs.
- **Key management:** Shared secret must be available to both the operator (at signing time) and the filter pipeline (at verification time). For a GitHub Actions-based filter, this means a repository secret.

**Operator friction:** Medium. Without tooling, computing an HMAC requires a command like `echo -n "body" | openssl dgst -sha256 -hmac "secret"`. With a CLI helper (`swain intake sign`), friction drops to low. The signature line is an HTML comment, so it renders invisibly in the GitHub issue UI.

**Implementation complexity:** Low. HMAC computation is a single function call in every language. The canonicalization step is the only non-trivial part.

### 2. GitHub-Native Trust Signals

#### 2a. Author Association (`author_association` field)

**How it works:** Every GitHub issue and comment carries an `author_association` field with one of: `OWNER`, `MEMBER`, `COLLABORATOR`, `CONTRIBUTOR`, `FIRST_TIMER`, `FIRST_TIME_CONTRIBUTOR`, `MANNEQUIN`, or `NONE`. The filter chain checks this field and fast-tracks issues from trusted associations.

**What the values mean:**
- `OWNER` -- the repo owner (personal repo) or organization owner
- `MEMBER` -- member of the organization that owns the repo
- `COLLABORATOR` -- has been explicitly added as a collaborator
- `CONTRIBUTOR` -- has a merged PR in the repo
- `NONE` -- no relationship

**Security properties:**
- **Replay-proof:** N/A -- there is no token to replay. Trust is identity-based.
- **Content-bound:** No -- any issue from a trusted author is fast-tracked regardless of content. A compromised account submits arbitrary work.
- **Spoofability:** The `author_association` field is set by GitHub's API and cannot be forged by the issue author. However, it depends on the author's GitHub account security. If an attacker compromises a collaborator's account, they bypass all filters.
- **Granularity:** Coarse. You cannot distinguish "this specific issue is operator-sanctioned" from "this person happens to be a collaborator." All issues from trusted authors get fast-tracked, including mistakes, drafts, or accidental submissions.

**Operator friction:** Zero. The operator just creates an issue normally. No signing, no tokens, no extra steps.

**Implementation complexity:** Trivial. The webhook payload or API response already includes `author_association`. A single string comparison.

**Assessment:** Author association is an excellent *first filter* for the slow path (e.g., auto-close issues from `NONE` authors on repos with restricted intake). But it is too coarse for the fast path -- it cannot distinguish intentional intake requests from casual issues filed by the same person. Best used as a complement to a content-bound mechanism, not a replacement.

#### 2b. GitHub App Payloads

**How it works:** A GitHub App installed on the repo receives webhook events for issue creation. The webhook payload is signed by GitHub using the App's webhook secret (`X-Hub-Signature-256` header). The filter pipeline, running as the App's webhook handler, can trust the payload's integrity and origin.

**Security properties:**
- **Replay-proof:** Yes -- GitHub includes a delivery GUID and timestamp. The handler can enforce idempotency.
- **Content-bound:** Yes -- the signature covers the entire payload including the issue body.
- **Trust model:** Strong -- GitHub is the signing authority. No shared secret between operator and filter (the App secret is between GitHub and the handler).

**But there is a fundamental mismatch.** The App signs the *delivery of the event*, not the *intent of the operator*. Any issue creation triggers the webhook, including issues from untrusted authors. The App signature proves "GitHub delivered this event" not "the operator sanctioned this issue." To use this for auth, the operator would need to create issues *through* the App (e.g., a custom UI or CLI that calls the App's API), which adds significant friction and complexity.

**Operator friction:** High if the operator must use the App to create issues. Medium if the App is used only for payload integrity on the receiving end (but then it does not solve auth).

**Implementation complexity:** High. Requires creating and hosting a GitHub App, handling webhook delivery, managing App credentials, and potentially building a custom issue-creation frontend.

**Assessment:** GitHub App payloads solve *transport integrity* (proving the event came from GitHub) but not *operator intent* (proving the operator sanctioned this specific issue). They are valuable as infrastructure for the filter pipeline but do not replace an auth mechanism on the issue content itself.

#### 2c. Commit-Signed References

**How it works:** The operator creates a signed commit (GPG or SSH signature) that contains or references the issue body, then includes the commit hash in the issue. The filter verifies: (1) the commit exists in the repo, (2) the commit signature is valid and from a known key, and (3) the commit content matches the issue body.

**Security properties:**
- **Replay-proof:** Yes -- the commit hash is unique. Reusing a hash with different content fails.
- **Content-bound:** Partial -- depends on how tightly the commit content is bound to the issue body. If the commit contains the full issue body, it is fully content-bound. If it only contains a hash or summary, it is weakly bound.
- **Trust model:** Strong -- GPG/SSH signatures are well-understood and widely deployed.

**Practical problems:**
- The operator must create a commit *before* filing the issue. This inverts the natural workflow (file issue, then do work, then commit).
- The commit must be pushed to the repo before the filter can verify it. This means the operator needs write access to some branch, or a fork.
- Commit signing requires GPG or SSH key setup, which is a one-time cost but non-trivial.
- The commit is "empty" (it exists only to sign the issue body), polluting the git history.

**Operator friction:** High. Multiple steps: compose issue body, create signed commit with body as content, push commit, file issue referencing commit hash. A CLI helper could streamline this, but the fundamental workflow inversion remains.

**Implementation complexity:** Medium. Verifying commit signatures via the GitHub API (`GET /repos/{owner}/{repo}/git/commits/{sha}` with `verification` field) is straightforward. Matching commit content to issue body requires canonicalization.

**Assessment:** Overly complex for the problem. The workflow inversion is a dealbreaker for routine use. Could work for high-ceremony scenarios (e.g., security-critical intake) but not as the default mechanism.

### 3. Asymmetric Signature Approach

**How it works:** The operator holds a private key (Ed25519 or RSA). The corresponding public key is stored in the repo (e.g., `.swain/intake-pubkey.pem` or in a config file). To create an authenticated issue, the operator signs the issue body with their private key and appends the signature as a footer: `<!-- swain-auth: ed25519:<base64-signature> -->`.

The filter extracts the signature, strips it from the body, and verifies using the public key from the repo.

**Security properties:**
- **Replay-proof:** Yes -- the signature is bound to the exact body content.
- **Content-bound:** Yes -- any modification invalidates the signature.
- **No shared secret:** The private key never leaves the operator's machine. The public key in the repo is not sensitive. Compromising the filter pipeline does not compromise the signing key.
- **Forward security:** If the operator rotates keys, old signatures remain valid against old public keys (if retained) or can be invalidated.
- **Non-repudiation:** The operator cannot deny having created a signed issue (assuming their private key was not compromised).

**Signature size concerns:** Ed25519 signatures are 64 bytes, which base64-encodes to 88 characters. An HTML comment footer like `<!-- swain-auth: ed25519:ABCD...XYZ= -->` is approximately 110 characters -- long but not unreasonable. RSA-2048 signatures are 256 bytes (344 chars base64), which is bulky. **Ed25519 is the clear choice.**

**Canonicalization:** Same challenge as HMAC. The signing tool must produce a canonical form that survives GitHub's markdown processing. The same mitigation applies: sign-then-submit via API, or enforce strict canonical form.

**CLI helper:** A helper like `swain intake sign "issue body"` or `swain intake sign --file issue.md` would:
1. Read the issue body
2. Canonicalize it (strip trailing whitespace, normalize line endings)
3. Sign with the operator's private key (from `~/.swain/intake-key` or configured path)
4. Append the signature footer
5. Optionally submit directly via `gh issue create`

This reduces the workflow to a single command, bringing friction from "high" to "low."

**Operator friction:** High without tooling (manual signing, base64 encoding, footer formatting). Low with a CLI helper. The one-time setup (key generation, adding public key to repo config) is comparable to setting up SSH keys.

**Implementation complexity:** Medium. Ed25519 verification is available in most languages (Go: `crypto/ed25519`, Python: `cryptography` or `PyNaCl`, Node: `crypto`). Key management adds a small amount of configuration surface.

### 4. Comparison Matrix

| Mechanism | Replay-proof | Content-bound | Operator friction | Impl. complexity | Secret management | Degradation mode |
|-----------|:---:|:---:|:---:|:---:|---|---|
| **TOTP** | No (30s window) | No | Low (paste 6 digits) | Low | Shared secret (TOTP seed) | Attacker who sees code has 30s to replay |
| **HMAC-SHA256** | Yes | Yes | Medium (need CLI tool) | Low | Shared secret (HMAC key) | Shared secret compromise = full bypass |
| **Author allowlist** | N/A | No | None | Trivial | None (GitHub identity) | Compromised account = full bypass; no per-issue granularity |
| **GitHub App** | Yes | Yes (transport) | High (custom workflow) | High | App credentials (GitHub-managed) | Proves delivery, not operator intent |
| **Commit-signed ref** | Yes | Partial | High (workflow inversion) | Medium | GPG/SSH key pair | Pollutes git history; awkward workflow |
| **Asymmetric sig** | Yes | Yes | Low (with CLI) / High (without) | Medium | Key pair (private stays local) | Strongest auth; key rotation is clean |

### 5. Narrative Analysis

**The field narrows quickly.** TOTP is unsuitable -- the replay window is a real vulnerability on public repos where automated watchers can extract and reuse codes within seconds (see Findings: TOTP-in-the-Clear Assessment above). Commit-signed references impose an unacceptable workflow inversion. GitHub App payloads solve transport integrity but not operator intent, and carry high implementation cost for a problem that does not require a hosted service.

**Three viable mechanisms remain:** author allowlist, HMAC, and asymmetric signatures.

**Author allowlist is the pragmatic baseline.** It costs nothing to implement, adds zero operator friction, and handles the common case where the repo has a small number of known operators. Its weakness is granularity: it fast-tracks *all* issues from trusted authors, including accidental or draft submissions. For a single-operator repo (swain's current reality), this weakness is minimal. For multi-contributor repos, it becomes a real concern.

**HMAC is the practical middle ground.** It provides content-binding and replay-proofing at low implementation cost. The shared secret is the main drawback -- if the secret leaks, an attacker can forge authenticated issues until the secret is rotated. However, for a system where the secret lives in a GitHub Actions secret and the operator's local config, the attack surface is small. A CLI helper makes friction comparable to TOTP.

**Asymmetric signatures are the strongest mechanism.** No shared secret means compromising the filter pipeline does not compromise auth. Ed25519 signatures are compact enough for an HTML comment footer. The key management burden (generate key pair, store public key in repo, store private key locally) is a one-time cost comparable to SSH setup. With a CLI helper, per-issue friction is low.

**Recommended layering for INITIATIVE-008:**

1. **Tier 0 (always active):** Author allowlist via `author_association`. Issues from `OWNER`/`MEMBER`/`COLLABORATOR` enter a *warm path* -- they skip spam/content filters but still go through structural validation. This is not full fast-path auth but a trust signal that reduces false-positive filtering.

2. **Tier 1 (default auth for fast path):** HMAC-SHA256 signature in an HTML comment footer. The `swain intake` CLI computes the HMAC and optionally submits the issue. This gives content-binding and replay-proofing at minimal implementation cost. The shared secret is acceptable for the current threat model (single-operator, attacker must compromise GitHub Actions secrets or operator's local config).

3. **Tier 2 (upgrade path):** Asymmetric Ed25519 signatures, same footer format. This becomes worthwhile if swain supports multi-operator intake (different operators with different keys) or if the threat model escalates. The CLI helper and footer format are designed to be mechanism-agnostic, so switching from HMAC to Ed25519 is a config change, not an architecture change.

**Key design decision: mechanism-agnostic footer format.** The auth footer should use a tagged format that identifies the mechanism:

```
<!-- swain-auth: hmac-sha256:<hex-digest> -->
<!-- swain-auth: ed25519:<base64-signature> -->
```

This allows the filter chain to support multiple mechanisms simultaneously and enables smooth migration from HMAC to asymmetric signatures without a flag day.

**What about canonicalization?** Both HMAC and asymmetric approaches share the canonicalization challenge. The recommended approach: the `swain intake` CLI creates the issue via the GitHub API, retrieves the rendered body, computes the signature over the API-returned body, and then edits the issue to append the footer. This two-step process (create-then-sign) eliminates canonicalization guesswork at the cost of a brief window where the issue exists unsigned. Alternatively, the CLI can enforce a strict canonical form (UTF-8, LF, no trailing whitespace, no HTML) and document that operators must not use GitHub's web editor for authenticated issues.

## Recommendation

### Verdict: HMAC-SHA256 with author-allowlist warm path

**TOTP is a NO-GO.** The polling architecture fundamentally breaks TOTP's security model — codes are always expired by polling time, one-time-use is unenforceable in batch processing, and codes posted in public issues are trivially replayable within the 60-90 second window. TOTP provides the appearance of authentication without substance and should not be adopted.

**HMAC-SHA256 is the recommended default auth mechanism for the fast path.** It is replay-proof (signature bound to exact issue content), content-bound (body modifications invalidate the signature), low implementation complexity (single function call), and the shared-secret model is acceptable for the current threat profile (single operator, secret stored in GitHub Actions secrets and operator's local config). A CLI helper (`swain intake sign`) reduces operator friction to a single command. The signature is invisible in the GitHub UI (HTML comment footer), keeping issues readable.

**Author allowlist (`author_association`) serves as a warm path — not full fast-path auth, but a trust-based filter bypass.** Issues from OWNER/MEMBER/COLLABORATOR skip spam and content-pattern filters but still go through structural validation. This handles the common case (operator filing issues from their own account) with zero friction. Its weakness — no per-issue granularity — is acceptable for single-operator repos and is compensated by HMAC for intentional fast-tracking.

### What this defends against

| Threat | Defended? | How |
|--------|-----------|-----|
| Drive-by spam | Yes | Author allowlist rejects unknown authors; HMAC rejects unsigned issues |
| Targeted spoofing | Mostly | HMAC signature cannot be forged without the shared secret; author allowlist blocks unknown actors |
| TOTP replay | N/A | TOTP is not used |
| Bot flooding | Yes | Author allowlist + rate limits reject bulk automated issues |
| Prompt injection | Partially | Fast path still exposes the classifying agent to issue body content; HMAC proves operator intent but not content safety |

### What this does NOT defend against

- **Compromised shared secret:** If the HMAC key leaks (GitHub Actions secret exposure, operator machine compromise), an attacker can forge authenticated issues until the key is rotated. Mitigation: key rotation procedure, monitoring for unexpected authenticated issues.
- **Compromised operator account:** If the operator's GitHub account is compromised, the author allowlist is bypassed. Mitigation: GitHub 2FA, token scoping.
- **Prompt injection via authenticated issues:** A legitimate operator (or someone with the HMAC secret) can submit issues with adversarial content that manipulates the classifying agent. Mitigation: out of scope for this spike (INITIATIVE-004 territory); content sanitization in the classifying agent.

### Residual risks and acceptability

The residual risks are acceptable because:
1. **Blast radius is bounded.** Even a successful attack only creates an unwanted artifact. The operator reviews all artifacts before execution. No code runs, no deployments happen, no data is exfiltrated.
2. **Key rotation is straightforward.** Changing the HMAC secret in GitHub Actions secrets and operator config invalidates all old signatures. No flag day needed.
3. **Upgrade path exists.** The mechanism-agnostic footer format (`<!-- swain-auth: <mechanism>:<value> -->`) means migrating from HMAC to Ed25519 asymmetric signatures is a config change. Ed25519 eliminates the shared-secret risk entirely and should be adopted when multi-operator intake or escalated threat models arise.

### Migration path

If the auth mechanism needs to change:
1. **HMAC → Ed25519:** Add Ed25519 verification to the filter chain alongside HMAC. Both mechanisms coexist (footer format distinguishes them). Deprecate HMAC after migration window.
2. **Single operator → multi-operator:** Each operator gets their own key pair. The filter chain checks against a list of public keys. Author allowlist becomes essential (maps GitHub identity to expected signing key).
3. **Secret compromise:** Rotate the HMAC key in GitHub Actions secrets and operator config. Old signatures become invalid. Re-sign any open issues that should remain authenticated.

## Integration Sketch

### Where auth fits in the EPIC-024 filter chain

The auth check runs at **step 3** of the filter chain defined in EPIC-024. The updated flow:

```
1. FETCH     — query open issues by pollLabel from configured repos
2. DEDUP     — skip issues with processedLabel
3. AUTH      — check for swain-auth footer → fast path or warm path
   ├─ HMAC valid       → FAST PATH (skip to step 6)
   ├─ author_association ∈ {OWNER,MEMBER,COLLABORATOR} → WARM PATH (skip to step 5)
   └─ neither          → SLOW PATH (continue to step 4)
4. AUTHOR    — check author against allowlist
5. CONTENT   — match required/excluded content patterns
6. CLASSIFY  — agent determines artifact type (SPEC/EPIC/SPIKE)
7. MARK      — label issue as processed, comment with artifact link
```

The warm path skips the author allowlist check (step 4) since `author_association` is a stronger signal, but still goes through content pattern matching (step 5) to catch accidental or draft submissions.

### Configuration shape

Extends the `intake` key in `swain.settings.json`:

```json
{
  "intake": {
    "repos": ["owner/repo"],
    "pollLabel": "agent-intake",
    "processedLabel": "intake-processed",
    "auth": {
      "method": "hmac-sha256",
      "secretEnvVar": "SWAIN_INTAKE_HMAC_SECRET"
    },
    "warmPathAssociations": ["OWNER", "MEMBER", "COLLABORATOR"],
    "authors": ["cristoslc"],
    "contentPatterns": {
      "required": [],
      "excluded": ["\\[question\\]", "\\[discussion\\]"]
    },
    "cronSchedule": "*/15 * * * *"
  }
}
```

Key changes from the original design:
- `authMethod: "totp"` replaced with `auth.method: "hmac-sha256"` and `auth.secretEnvVar` pointing to the GitHub Actions secret name
- `warmPathAssociations` added to configure which `author_association` values qualify for the warm path
- `authors` remains for the slow-path allowlist (step 4)

### Auth validation pseudocode

```python
def check_auth(issue: GitHubIssue, config: IntakeConfig) -> AuthResult:
    """Deterministic auth check — no LLM involvement."""

    # Check for swain-auth footer
    footer_match = re.search(
        r'<!-- swain-auth: (\w[\w-]+):(\S+) -->',
        issue.body
    )

    if footer_match:
        mechanism = footer_match.group(1)  # e.g., "hmac-sha256"
        signature = footer_match.group(2)  # e.g., hex digest

        if mechanism == "hmac-sha256":
            # Strip the footer to get the signed body
            signed_body = issue.body[:footer_match.start()].rstrip()
            secret = os.environ[config.auth.secretEnvVar]
            expected = hmac.new(
                secret.encode(), signed_body.encode(), hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(signature, expected):
                return AuthResult.FAST_PATH

        elif mechanism == "ed25519":
            # Future: verify Ed25519 signature against public key
            pass

    # Check warm path (author association)
    if issue.author_association in config.warmPathAssociations:
        return AuthResult.WARM_PATH

    # Fall through to slow path
    return AuthResult.SLOW_PATH
```

### How the operator submits an authenticated issue

**With the CLI helper (recommended):**

```bash
# One-command workflow
swain intake create --repo owner/repo \
  --title "[SPEC] Add rate limiting to API" \
  --body-file issue.md \
  --label agent-intake

# What happens under the hood:
# 1. Reads issue body from issue.md
# 2. Canonicalizes (UTF-8, LF, strip trailing whitespace)
# 3. Computes HMAC-SHA256 with secret from ~/.swain/intake.json
# 4. Appends <!-- swain-auth: hmac-sha256:<digest> --> footer
# 5. Creates issue via `gh issue create`
```

**Without the CLI helper (manual):**

```bash
# 1. Write your issue body
cat > /tmp/issue.md << 'BODY'
Implement rate limiting for the public API endpoints...
BODY

# 2. Compute HMAC
HMAC=$(cat /tmp/issue.md | openssl dgst -sha256 -hmac "$SWAIN_INTAKE_HMAC_SECRET" | awk '{print $NF}')

# 3. Append footer and create issue
echo "" >> /tmp/issue.md
echo "<!-- swain-auth: hmac-sha256:$HMAC -->" >> /tmp/issue.md
gh issue create --repo owner/repo --title "[SPEC] Rate limiting" --body-file /tmp/issue.md --label agent-intake
```

### How failed auth routes to the slow path

A failed auth check does NOT reject the issue. It routes to the slow path:

- **Missing footer:** No `<!-- swain-auth: ... -->` found → slow path (author allowlist + content patterns)
- **Invalid signature:** Footer present but HMAC doesn't match → slow path (treat as unsigned; the signature may have been corrupted by editing)
- **Unknown mechanism:** Footer specifies an unrecognized mechanism → slow path (forward-compatible; new mechanisms added later won't break old filters)

The slow path is the default, not a failure mode. Most issues (questions, discussions, feature requests from community members) will take the slow path and be filtered by author allowlist and content patterns. The fast path is an optimization for the operator's own authenticated submissions.
