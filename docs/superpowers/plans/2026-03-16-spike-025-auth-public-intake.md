# SPIKE-025: Authentication for Public Intake Channels — Research Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a GO/NO-GO recommendation on TOTP-in-the-clear for public GitHub issue intake, evaluate alternative auth mechanisms, and deliver a threat model + integration sketch for the chosen mechanism.

**Architecture:** This is a research spike — no code. Five research tasks producing documented findings in the spike artifact. Each task appends a findings section to the spike document. The final task synthesizes findings into a recommendation.

**Tech Stack:** Web research, GitHub API docs, TOTP/HMAC/cryptographic primitive analysis, markdown documentation

**Spec:** `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`
**Design context:** `docs/superpowers/specs/2026-03-16-automated-work-intake-design.md`

---

## File Map

### Modified files
- `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md` — All findings appended here

---

## Chunk 1: Threat Model and Mechanism Evaluation

### Task 1: Define the threat model

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Research and document the threat model for authenticated intake on public repos. The output is a `## Findings: Threat Model` section appended to the spike artifact.

- [ ] **Step 1: Identify threat actors and attack vectors**

Document these specific scenarios:
- **Drive-by spam:** Random user opens an issue with a valid-looking format, triggering agent work on garbage input
- **Targeted spoofing:** Attacker watching the repo crafts a legitimate-looking issue to inject malicious work (e.g., "implement backdoor in auth module")
- **TOTP replay:** Attacker observes a TOTP code in a public issue and submits a competing issue with the same code before the window expires
- **Bot automation:** Automated scripts mass-filing issues to overwhelm the intake pipeline
- **Social engineering:** Issue content designed to manipulate the classifying agent (prompt injection via issue body)

For each, document: likelihood, impact, and whether the slow-path filters (author allowlist, label, content patterns) already mitigate it.

- [ ] **Step 2: Document trust assumptions**

What do we trust and not trust?
- GitHub's author identity (can a GitHub username be spoofed?)
- GitHub's API rate limits (do they throttle issue creation enough to prevent flooding?)
- The 30-second TOTP window (how fast can an attacker observe + act?)
- Label permissions (who can add labels to issues on public repos?)

Research GitHub's actual behavior for each. Use the GitHub API docs and security documentation.

- [ ] **Step 3: Write the threat model section**

Append a `## Findings: Threat Model` section to the spike artifact with:
- Threat actor table (actor, motivation, capability)
- Attack vector table (vector, likelihood, impact, existing mitigation)
- Trust assumptions with evidence from GitHub docs

- [ ] **Step 4: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): document threat model for public intake auth"
```

---

### Task 2: Evaluate TOTP-in-the-clear

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Analyze whether TOTP codes posted in public GitHub issues are viable as a fast-track authentication mechanism.

- [ ] **Step 1: Research TOTP replay window mechanics**

Document:
- Standard TOTP window (RFC 6238): 30 seconds, with typical implementations accepting ±1 window (90 seconds effective)
- Time from issue creation to GitHub API visibility (webhook latency, API indexing delay)
- Time for an attacker to: see the issue, extract the code, create a competing issue
- Whether GitHub issues are instantly visible via API/webhooks or if there's propagation delay

- [ ] **Step 2: Analyze one-time-use enforcement**

Can the intake pipeline mark a TOTP code as "consumed" to prevent replay?
- The pipeline runs on a schedule (e.g., every 15 minutes), not in real-time
- Multiple issues with the same TOTP code could arrive between polling intervals
- Document whether one-time-use is enforceable in a polling (not real-time) architecture
- Consider: if polling interval > TOTP window, the code is already expired by the time it's checked — does this help or hurt?

- [ ] **Step 3: Assess practical risk**

Given the threat model from Task 1, rate the practical risk of TOTP replay:
- How likely is an attacker to be watching issue creation in real-time?
- What's the actual damage if a replayed TOTP issue passes the fast path? (It still goes to an agent that creates an artifact — the operator reviews artifacts before execution)
- Is the risk acceptable given the two-tier model (fast path is a convenience, not a security boundary)?

- [ ] **Step 4: Write GO/NO-GO assessment**

Append a `## Findings: TOTP-in-the-Clear Assessment` section:
- Replay window analysis with timing diagram
- One-time-use feasibility in polling architecture
- Practical risk rating (low/medium/high) with justification
- **GO** if: risk is low and acceptable given the two-tier model
- **NO-GO** if: risk is medium+ or the mechanism provides false confidence

- [ ] **Step 5: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): TOTP-in-the-clear GO/NO-GO assessment"
```

---

### Task 3: Evaluate alternative auth mechanisms

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Research and compare alternative authentication primitives that work on public repos.

- [ ] **Step 1: Research HMAC signatures over issue body**

Document:
- How it works: operator computes `HMAC-SHA256(secret, issue_body)` and includes the signature in the issue
- Verification: filter chain recomputes HMAC and compares
- Pros: no replay window (signature is bound to content), no timing dependency
- Cons: operator needs tooling to compute HMAC before submitting, secret must be shared with the filter pipeline
- Usability: how would the operator include the signature? (footer line, hidden comment, etc.)
- Can an attacker reverse-engineer the secret from observed signature + body pairs?

- [ ] **Step 2: Research GitHub-native trust signals**

Document:
- **Author verification:** GitHub's `author_association` field on issues (OWNER, MEMBER, COLLABORATOR, CONTRIBUTOR, NONE). Is this sufficient for the fast path?
- **GitHub App payloads:** Can a GitHub App sign issue creation events? Would this require the operator to use the App to create issues?
- **Commit-signed references:** Issue body references a signed commit hash. Filter verifies the commit exists and is signed by a known key.
- For each: implementation complexity, operator friction, security properties

- [ ] **Step 3: Research asymmetric signature approach**

Document:
- Operator signs the issue body (or a hash of it) with a private key, includes the signature in the issue
- Filter chain verifies with the corresponding public key (stored in repo config)
- Pros: strongest auth, no shared secret, signature bound to content
- Cons: highest operator friction (need signing tooling), signature is long and ugly in issue body
- Could this be simplified with a CLI helper? e.g., `swain intake sign "issue body"` → outputs body + signature

- [ ] **Step 4: Write comparison matrix**

Append a `## Findings: Alternative Auth Mechanisms` section:

| Mechanism | Replay-proof | Content-bound | Operator friction | Implementation complexity | Secret management |
|-----------|-------------|---------------|-------------------|--------------------------|-------------------|
| TOTP | No (window) | No | Low (paste code) | Low | Shared secret |
| HMAC | Yes | Yes | Medium (compute hash) | Low | Shared secret |
| Author allowlist | N/A | N/A | None | Trivial | None (GitHub identity) |
| GitHub App | Yes | Yes | Medium (use App) | High | App credentials |
| Commit-signed ref | Yes | Partial | High (create commit) | Medium | GPG/SSH key |
| Asymmetric sig | Yes | Yes | High (sign body) | Medium | Key pair |

Include a narrative analysis — not just the table — explaining which mechanisms best fit the constraints (public repo, operator-friendly, deterministic validation).

- [ ] **Step 5: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): evaluate alternative auth mechanisms"
```

---

## Chunk 2: Recommendation and Integration

### Task 4: Synthesize recommendation

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Combine findings from Tasks 1-3 into a clear recommendation.

- [ ] **Step 1: Select recommended mechanism**

Based on the threat model, TOTP assessment, and alternatives comparison, select the recommended auth mechanism. Consider:
- The two-tier model means the fast path is a convenience optimization, not a hard security boundary
- The slow path (author allowlist + labels + content patterns) is the baseline security
- The auth mechanism's primary job is proving operator intent, not preventing all attack vectors
- Operator friction matters — a mechanism nobody uses is worse than a weaker one that gets used

- [ ] **Step 2: Write the recommendation section**

Append a `## Recommendation` section:
- Recommended mechanism with rationale (2-3 paragraphs)
- What it defends against and what it doesn't (referencing threat model)
- Residual risks and why they're acceptable
- Migration path if the mechanism needs to change later

- [ ] **Step 3: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): synthesize auth mechanism recommendation"
```

---

### Task 5: Write integration sketch and close spike

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Show how the recommended mechanism plugs into EPIC-024's filter chain.

- [ ] **Step 1: Write the integration sketch**

Append a `## Integration Sketch` section showing:
- Where in the filter chain (step 3 of EPIC-024) the auth check runs
- What the config shape looks like for the recommended mechanism (extending the `intake.authMethod` field in `swain.settings.json`)
- Pseudocode for the auth validation function (deterministic, no LLM)
- How the operator submits an authenticated issue (step-by-step)
- How a failed auth check routes to the slow path (not rejection)

- [ ] **Step 2: Update spike status and lifecycle**

Update the spike frontmatter:
- `status: Proposed` → `status: Active` (or `Complete` if all findings are documented)
- Add lifecycle entry for research completion

- [ ] **Step 3: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): integration sketch and spike completion"
```

- [ ] **Step 4: Verify all expected outputs are present**

Check the spike artifact contains all four expected outputs:
1. GO/NO-GO on TOTP-in-the-clear for public repos
2. Recommended auth mechanism with rationale
3. Threat model summary for the chosen mechanism
4. Integration sketch showing how the auth check fits into the filter chain

If any are missing, fill gaps before closing.
