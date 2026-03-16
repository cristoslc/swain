---
title: "Project Identity Enforcement"
artifact: SPEC-054
track: implementable
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - EPIC-020
depends-on-artifacts: []
addresses:
  - INITIATIVE-005
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Project Identity Enforcement

## Problem Statement

When an operator runs multiple concurrent agents across different projects, there is no mechanism to prevent them from accidentally prompting the wrong agent with tasks intended for a different project. Two distinct failure modes exist:

1. **Full project confusion** — the operator pastes a prompt into the wrong terminal window entirely. The agent happily pulls context, creates artifacts, modifies code, and commits — all in the wrong repository. This has happened in practice and was only discovered at merge time, after significant work was done in the wrong codebase. This is the primary and most dangerous failure mode.

2. **Worktree confusion** — the operator has multiple worktrees for the same project and prompts the wrong one. Less dangerous (same repo) but still wastes work and can create conflicts.

Governance currently validates that swain skills and governance files are present, but never asks "am I the right agent for this task?" The agent has no concept of project identity and will execute any instruction it receives regardless of whether the work belongs to the project it's running in.

## External Behavior

### Inputs

- **Project fingerprint** — computed automatically from the git remote URL and repository root path at first session initialization
- **Session startup** — preflight checks run the fingerprint validation on every session start
- **Operator prompts** — ongoing prompts are compared against project context when feasible

### Outputs

- **Project identity file** — `.agents/project-identity.json` stored per-project, version-controlled
- **Governance declaration** — AGENTS.md includes an explicit `## Project Identity` section declaring the project name and scope, injected into the agent's system prompt so it always knows what project it belongs to
- **Session banner** — project name displayed prominently at session start (via swain-session)
- **Mismatch warning** — clear error surfaced when fingerprint validation fails
- **Scope drift warning** — advisory when the agent detects incoming work that references unknown artifacts, repos, or domains not associated with this project

### Preconditions

- Git repository with at least one remote configured (fallback: repo root directory name)
- `.agents/` directory exists (ensured by swain-doctor)

### Postconditions

- Every swain-managed project has a stable, deterministic project identity
- Preflight detects and warns on project identity mismatches
- Operator sees which project/agent they're interacting with at session start

### Constraints

- Zero runtime dependencies — pure bash, no external tools beyond git
- Must not break existing projects — graceful first-run initialization
- Must work in worktrees (fingerprint derived from main repo, not worktree path)
- File must be version-controlled so all agents on the same project share the identity

## Acceptance Criteria

**AC-1: Fingerprint generation**
Given a git repository with a remote origin
When swain-doctor runs for the first time
Then it creates `.agents/project-identity.json` with fields: `projectName`, `remoteUrl`, `fingerprint` (SHA-256 of remote URL), `createdAt`

**AC-2: Fingerprint validation on session start**
Given `.agents/project-identity.json` exists
When preflight runs
Then it computes the current fingerprint and compares to the stored one
And exits 0 if they match, exits 1 with a clear warning if they don't

**AC-3: Session banner includes project name**
Given a valid project identity
When swain-session initializes
Then the session greeting includes the project name (e.g., "swain" not the full path)

**AC-4: Graceful first-run**
Given a project with no `.agents/project-identity.json`
When swain-doctor runs
Then it creates the file without prompting (no migration needed — this is additive)

**AC-5: Worktree resilience**
Given an agent running in a git worktree
When fingerprint is computed
Then it uses `git rev-parse --path-format=absolute --git-common-dir` to resolve the main repo
And the fingerprint matches the main checkout's fingerprint

**AC-6: No-remote fallback**
Given a git repository with no remotes
When fingerprint is computed
Then it falls back to the repository root directory name as the project name
And uses the absolute path hash as the fingerprint

**AC-7: Mismatch produces actionable guidance**
Given a fingerprint mismatch (e.g., `.agents/` copied from another project)
When preflight detects it
Then the warning includes: expected project name, actual project name, and instructions to regenerate

**AC-8: Governance declares project identity**
Given a project with a valid `.agents/project-identity.json`
When swain-doctor runs (or governance is injected/refreshed)
Then AGENTS.md includes a `## Project Identity` section with the project name, repository URL, and a directive: "You are the agent for project {name}. If a task does not appear to relate to this project, confirm with the operator before executing."

**AC-9: Scope drift detection on incoming work**
Given the agent has a project identity loaded from governance
When the operator's prompt references a repository, project name, or artifact namespace that does not match the current project
Then the agent asks for confirmation: "This appears to be work for {other}, but you're in {this project}. Continue?"
And waits for explicit confirmation before proceeding

**AC-10: Scope drift signal vocabulary**
The agent should treat the following as scope drift signals requiring confirmation:
- References to git remotes not configured in the current repo
- References to artifact IDs (SPEC-xxx, EPIC-xxx) that don't exist in `docs/`
- Explicit mentions of a different project name (e.g., "in the billing-service repo")
- Requests to `cd` or operate outside the project root
- Requests to clone, pull from, or push to a different repository

## Scope & Constraints

**In scope:**
- Project fingerprint computation and storage
- Governance-level project identity declaration (AGENTS.md section)
- Preflight validation of fingerprint
- Session banner enhancement to show project name
- Scope drift detection and confirmation prompt
- swain-doctor first-run initialization

**Out of scope:**
- Hard blocking of cross-project work (confirmation is sufficient — the operator may intentionally do cross-project work)
- Agent instance tracking (which terminal session is which) — related but distinct; see EPIC-020
- Cross-machine identity (fingerprints are git-remote-based, naturally portable)
- NLP-level prompt classification (scope drift detection uses structural signals like artifact IDs and repo names, not semantic analysis)

## Implementation Approach

### TDD Cycle 1: Fingerprint computation (AC-1, AC-5, AC-6)
- Test: script computes deterministic fingerprint from git remote URL
- Test: worktree produces same fingerprint as main checkout
- Test: no-remote fallback uses directory name
- Implement: `scripts/project-fingerprint.sh` — pure bash, outputs JSON

### TDD Cycle 2: Preflight integration (AC-2, AC-7)
- Test: preflight exits 0 when fingerprint matches
- Test: preflight exits 1 with warning when mismatch
- Test: preflight exits 0 when no identity file (first run — doctor handles creation)
- Implement: add fingerprint check to `swain-preflight.sh`

### TDD Cycle 3: Doctor initialization + governance injection (AC-4, AC-8)
- Test: doctor creates identity file when missing
- Test: doctor does not overwrite existing identity file
- Test: AGENTS.md contains `## Project Identity` section after doctor runs
- Test: governance section includes project name and scope directive
- Implement: add identity initialization to swain-doctor; add governance block to AGENTS.content.md template

### TDD Cycle 4: Session banner (AC-3)
- Test: swain-session reads project name from identity file
- Test: session greeting includes project name
- Implement: update swain-session startup to include project identity

### TDD Cycle 5: Scope drift detection (AC-9, AC-10)
- This is a governance rule, not a script — the `## Project Identity` section in AGENTS.md instructs the agent to check incoming prompts against the signal vocabulary (AC-10)
- Test: manually verify the agent asks for confirmation when given a prompt referencing a different project's artifacts
- The enforcement is in the agent's system prompt, not in bash — the governance declaration does the work

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | — | Initial creation; operator requested governance enforcement for multi-project safety |
