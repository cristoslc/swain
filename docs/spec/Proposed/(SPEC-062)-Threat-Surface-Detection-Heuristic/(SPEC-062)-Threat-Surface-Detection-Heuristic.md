---
title: "Threat Surface Detection Heuristic"
artifact: SPEC-062
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-023
linked-artifacts:
  - SPIKE-020
depends-on-artifacts: []
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# Threat Surface Detection Heuristic

## Problem Statement

swain-do needs to automatically classify whether a task touches a security-sensitive surface so it can activate security gates (EPIC-023) only when relevant. Without this classification, either every task gets security overhead (too noisy) or no task does (defeats the purpose). The heuristic must have a low false-positive rate to avoid security fatigue.

## External Behavior

**Input:** A tk task (title, description, tags, linked SPEC's acceptance criteria, file paths touched during implementation).

**Output:** Boolean `is_security_sensitive` plus a list of matched security surface categories.

**Security surface categories:**
- `auth` — authentication, authorization, session management, token handling
- `input-validation` — user input parsing, form handling, request deserialization
- `crypto` — encryption, hashing, key management, certificate handling
- `external-data` — API calls, database queries, file I/O from untrusted sources
- `agent-context` — AGENTS.md, CLAUDE.md, skill files, .cursorrules, MCP config
- `dependency-change` — package.json, requirements.txt, go.mod, Cargo.toml modifications
- `secrets` — .env files, credential files, API key references

**Detection signals (checked in order, first match wins):**
1. Task tags: `security`, `auth`, `crypto`, `input-validation`
2. Task title keywords: auth, login, password, token, secret, key, encrypt, certificate, permission, role, sanitize, validate, escape
3. SPEC acceptance criteria keywords: same keyword set
4. File paths touched: files matching security-sensitive patterns (auth/, crypto/, middleware/auth, .env, *credentials*, *secret*)

## Acceptance Criteria

- Given a task titled "Add JWT token validation middleware", when classified, then `is_security_sensitive` is true with category `auth`
- Given a task titled "Update README formatting", when classified, then `is_security_sensitive` is false
- Given a task with tag `security`, when classified, then `is_security_sensitive` is true regardless of title
- Given a task that modifies `package.json`, when classified, then `is_security_sensitive` is true with category `dependency-change`
- Given a task whose parent SPEC mentions "sanitize user input" in acceptance criteria, when classified, then `is_security_sensitive` is true with category `input-validation`
- False positive rate is below 20% on a sample of 20 non-security tasks from the project's tk history

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Heuristic only — no ML, no LLM calls for classification
- File path detection only works post-implementation (during completion gate), not at claim time
- At claim time, only title, tags, and SPEC criteria are available

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | -- | Decomposed from EPIC-023 |
