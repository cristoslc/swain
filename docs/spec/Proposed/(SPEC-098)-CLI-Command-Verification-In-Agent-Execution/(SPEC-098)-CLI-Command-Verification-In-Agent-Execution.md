---
title: "CLI Command Verification in Agent Execution"
artifact: SPEC-098
track: implementable
status: Proposed
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-016
parent-vision: VISION-001
linked-artifacts:
  - SPEC-092
  - SPEC-099
  - SPIKE-036
depends-on-artifacts:
  - SPIKE-036
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# CLI Command Verification in Agent Execution

## Problem Statement

Agents write shell scripts that invoke external CLIs (Docker, git, runtime tools) based on documentation assumptions. These assumptions are often wrong — flags don't exist, commands behave differently than expected, or interactive mode requirements are missed. The resulting scripts pass syntax checks (`sh -n`) but fail on first real use.

The swain-do execution workflow has TDD enforcement for application logic but no equivalent for verifying external CLI assumptions. A new verification step is needed in the implementation workflow.

## External Behavior

TBD — depends on SPIKE-036 findings. The verification mechanism will be integrated into the swain-do skill's execution workflow, likely as a step between plan creation and code writing.

## Acceptance Criteria

- Given an implementation plan that includes external CLI commands, when the agent begins implementation, then it verifies each external command's behavior before embedding it in a script
- Given the three bugs from the 2026-03-19 session, when the verification mechanism is applied retroactively, then at least 2 of 3 would have been caught
- Given the verification mechanism, when an agent writes a script with verified commands, then the script works on first real use

## Scope & Constraints

- Depends on SPIKE-036 for the verification approach
- Must integrate with swain-do's existing TDD enforcement, not replace it
- Must not significantly slow down implementation — verification should be fast (seconds, not minutes)

## Implementation Approach

TBD — depends on SPIKE-036 findings.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | — | Blocked on SPIKE-036 |
