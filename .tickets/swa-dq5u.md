---
id: swa-dq5u
status: closed
deps: []
links: []
created: 2026-03-16T19:17:41Z
type: task
priority: 1
assignee: cristos
parent: swa-1fd2
tags: [spec:SPIKE-025, spec:SPIKE-025]
---
# Task 3: Evaluate alternative auth mechanisms

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


## Notes

**2026-03-16T19:33:30Z**

Completed: evaluated 6 auth mechanisms with comparison matrix and narrative analysis
