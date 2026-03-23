---
title: "Cross-Platform Deny-Rule Portability"
artifact: SPIKE-041
track: container
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
question: "Can swain define a single set of governance-protection deny rules (no editing AGENTS.md, no modifying skill files, no tampering with .agents/ directory) and project them onto each platform's native deny mechanism with minimal per-platform configuration?"
gate: Pre-MVP
parent-initiative: INITIATIVE-020
risks-addressed:
  - Deny rule formats differ across platforms (JSON settings vs TOML policies vs Starlark rules vs config permissions)
  - Some platforms may not support path-level deny rules for all tool types
  - Governance file protection may be circumvented via Bash on platforms without sandbox
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - SPIKE-038
  - VISION-005
---

# Cross-Platform Deny-Rule Portability

## Summary

## Question

Can swain define a single set of governance-protection deny rules (no editing AGENTS.md, no modifying skill files, no tampering with .agents/ directory) and project them onto each platform's native deny mechanism with minimal per-platform configuration?

## Go / No-Go Criteria

- **Go**: A canonical deny-rule set (5–10 rules protecting governance files) can be translated to at least 3 platforms' native formats via a simple generator script, and the deny rules are verifiably unbypassable on those platforms
- **No-Go**: Deny rule semantics differ too much across platforms (e.g., one platform's deny doesn't cover Bash-invoked file operations, breaking the protection model)

## Pivot Recommendation

If portable deny rules are impractical, fall back to per-platform hand-maintained configurations checked into the repo (`.claude/settings.json`, `.gemini/policies/governance.toml`, `.codex/rules/governance.rules`, etc.) and use swain-doctor to validate they're in sync.

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
