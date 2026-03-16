---
id: swa-8pxx
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
# Task 1: Define the threat model

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


## Notes

**2026-03-16T19:29:33Z**

Completed: threat model documented with 5 threat actors, 5 attack vectors, and 4 trust assumptions with GitHub docs evidence
