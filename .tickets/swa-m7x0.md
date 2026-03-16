---
id: swa-m7x0
status: in_progress
deps: []
links: []
created: 2026-03-16T19:17:41Z
type: task
priority: 1
assignee: cristos
parent: swa-1fd2
tags: [spec:SPIKE-025, spec:SPIKE-025]
---
# Task 2: Evaluate TOTP-in-the-clear

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

