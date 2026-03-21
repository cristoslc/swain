---
title: "GitHub Token Scoping Mechanisms"
artifact: SPIKE-037
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
question: "Which GitHub authentication mechanism provides 'can create PRs and push to non-protected branches, cannot push to or merge into protected branches' — without relying solely on server-side branch protection rules?"
gate: Pre-MVP
risks-addressed:
  - An unattended agent with an over-permissioned token could push directly to main, bypassing review
  - Relying solely on branch protection rules creates a single point of failure — misconfiguration or repo transfer could silently remove the guard
  - Token theft from a compromised sandbox could grant broader access than intended
evidence-pool: ""
linked-artifacts:
  - EPIC-037
---

# GitHub Token Scoping Mechanisms

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

Which GitHub authentication mechanism provides "can create PRs and push to non-protected branches, cannot push to or merge into protected branches" — without relying solely on server-side branch protection rules?

## Go / No-Go Criteria

- **Go**: At least one mechanism provides client-side or token-level enforcement that prevents pushes to protected branches, independent of (or in addition to) server-side branch protection rules
- **Conditional Go**: All mechanisms rely on server-side branch protection, but one provides significantly tighter scoping than the others (e.g., repo-scoped vs. org-scoped, time-limited, auditable)
- **No-Go**: No mechanism provides meaningful scoping — the only defense is server-side branch protection, and token permissions are effectively "full repo access or nothing"

## Pivot Recommendation

If No-Go: investigate a proxy/gateway approach where the host intercepts git pushes from the sandbox and rejects pushes to protected refs before they reach GitHub. This would provide client-side enforcement regardless of token type.

## Findings

### Mechanisms to evaluate

1. **Fine-grained Personal Access Tokens (PATs)** — GitHub's newer token type with per-repository, per-permission scoping. Can scope to `pull_requests: write` + `contents: write` on specific repos. Question: can `contents: write` be further restricted to exclude pushes to specific branches?

2. **GitHub App installation tokens** — per-installation, per-repository, configurable permissions. More granular than PATs. Question: do app permissions distinguish between branch push targets, or is it "contents: write = all branches"?

3. **Deploy keys** — per-repository SSH keys with read-only or read-write access. Question: can read-write deploy keys be combined with branch protection to create a defense-in-depth model? Are they auditable per-sandbox?

4. **Git protocol proxy** — a host-side `git-receive-pack` wrapper or SSH forced command that rejects pushes to specific refs. Not a GitHub feature but a client-side enforcement layer. Question: feasible inside Docker container/sandbox networking?

### Evaluation criteria

For each mechanism, assess:
- **Granularity**: can it distinguish "push to feature branch" from "push to main"?
- **Independence**: does it work without server-side branch protection, or is it additive?
- **Provisioning**: can the host create it programmatically during `swain-box` startup?
- **Auditability**: can the operator see what the token was used for?
- **Revocability**: can the token be invalidated when the sandbox is torn down?
- **Signing compatibility**: does it work alongside `swain-keys` commit signing?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Initial creation — research token scoping for PR-only agent guardrails |
| Active | 2026-03-20 | -- | Approved for research |
