---
title: "Agent Implementation Reliability"
artifact: INITIATIVE-016
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-vision: VISION-001
priority-weight: high
success-criteria:
  - Agents verify assumptions about external CLI behavior before embedding commands in scripts
  - Shell scripts produced by agents do not contain untested Docker/git/runtime invocations
  - A repeatable verification mechanism exists that agents can invoke during implementation
linked-artifacts:
  - SPIKE-036
  - SPEC-098
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Agent Implementation Reliability

## Strategic Focus

Agents make assumptions about external tools (Docker CLI, git, runtime auth flows) and embed those assumptions directly in code without verification. In a single VISION-002 session, this produced three distinct bugs: `docker sandbox run <name> --version` hanging indefinitely (wrong probe command), `docker sandbox exec` without `-it` (shell exits immediately), and `--dangerously-skip-permissions` passed as container CMD instead of runtime arg. All three passed syntax checks but failed on first real use.

The problem isn't efficiency — it's reliability. An agent that ships broken scripts erodes operator trust faster than one that ships slowly. The verification gap is between "the code is syntactically valid" (which `sh -n` catches) and "the external commands do what the agent thinks they do" (which nothing catches today).

## Scope Boundaries

**In scope:** Verification mechanisms for external CLI assumptions during agent implementation. How agents probe, validate, and test commands that interact with Docker, git, runtime CLIs, and other external tools before writing them into scripts.

**Out of scope:** General code quality (covered by superpowers code review). Test coverage for business logic (covered by TDD enforcement). Static analysis for security (covered by INITIATIVE-004).

## Child Epics

None — scope is likely small enough for epic-less specs.

## Small Work (Epic-less Specs)

- SPIKE-036: External CLI Assumption Verification (Active) — research what verification mechanisms agents can use
- SPEC-098: CLI Command Verification in Agent Execution (Proposed) — implement findings into swain-do workflow

## Key Dependencies

None — this is a standalone quality initiative.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Created after three CLI assumption bugs in one VISION-002 session |
