---
title: "swain-doctor Security Integration"
artifact: SPEC-061
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-017
linked-artifacts: []
depends-on-artifacts:
  - SPEC-059
  - SPEC-060
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-doctor Security Integration

## Problem Statement

swain-doctor runs at session start to validate project health. Security scanning should be part of this preflight check — but the full swain-security-check scan is too heavy for every session start. A lightweight version is needed that catches the most critical issues (tracked secrets, missing .gitignore patterns, context-file injection) without the latency of full scanner invocation.

## External Behavior

**During swain-doctor preflight:**
1. Check scanner binary availability (per SPEC-059) — emit diagnostics for missing tools
2. Run the context-file scanner (SPEC-058) against AGENTS.md, CLAUDE.md, and any skill SKILL.md files in the current project — critical findings only (categories D, F, G, H — exfiltration, obfuscation, hidden Unicode, MCP manipulation)
3. Check for tracked `.env` files in git history (`git ls-files | grep -E '\.env($|\.)' | grep -v '\.example'`)

**Output:** Integrated into swain-doctor's existing diagnostic format. Security findings appear as `WARN` or `CRIT` severity diagnostics.

**Performance:** The lightweight check must complete in under 3 seconds to avoid slowing session start.

## Acceptance Criteria

- Given AGENTS.md contains a Category D pattern (data exfiltration), when swain-doctor runs, then a CRIT diagnostic is emitted with the finding details
- Given gitleaks is not installed, when swain-doctor runs, then an INFO diagnostic suggests the install command
- Given a tracked `.env` file exists in git history, when swain-doctor runs, then a WARN diagnostic is emitted with remediation guidance (git filter-branch or BFG)
- Given no security issues, when swain-doctor runs, then no security diagnostics appear (silent pass)
- The lightweight check adds less than 3 seconds to swain-doctor runtime

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Lightweight subset only — not the full multi-vector scan
- Does not block session start — diagnostics are advisory
- Depends on SPEC-059 (availability checks) and SPEC-060 (skill exists) but can be partially implemented with just SPEC-058 (context-file scanner)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | -- | Decomposed from EPIC-017 |
