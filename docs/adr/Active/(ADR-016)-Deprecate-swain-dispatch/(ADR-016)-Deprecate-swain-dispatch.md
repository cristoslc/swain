---
title: "Deprecate swain-dispatch"
artifact: ADR-016
track: standing
status: Active
author: cristos
created: 2026-03-25
last-updated: 2026-03-25
linked-artifacts:
  - SPEC-025
  - SPEC-029
  - SPEC-074
  - EPIC-010
depends-on-artifacts: []
trove: ""
---

# Deprecate swain-dispatch

## Context

swain-dispatch ([SPEC-025](../../spec/Complete/(SPEC-025)-Swain-Dispatch-Skill/(SPEC-025)-Swain-Dispatch-Skill.md), [EPIC-010](../../epic/Complete/(EPIC-010)-Agent-Dispatch-Via-GitHub-Issues/(EPIC-010)-Agent-Dispatch-Via-GitHub-Issues.md)) dispatched swain-design artifacts to background agents via GitHub Issues, using `anthropics/claude-code-action@v1` on GitHub Actions runners. The skill required an `ANTHROPIC_API_KEY` repository secret with per-token API billing.

Anthropic's Max and Pro subscription plans provide Claude Code access without per-token billing, but their credentials cannot be used as API keys in GitHub Actions workflows. Since the project operates on a Max/Pro subscription, swain-dispatch is non-functional without incurring separate API costs.

Additionally, two high-severity functional bugs were identified in the skill ([SPEC-074](../../spec/Abandoned/(SPEC-074)-Fix-Dispatch-Functional-Bugs/(SPEC-074)-Fix-Dispatch-Functional-Bugs.md)) — broken `repository_dispatch` triggering and broken heredoc variable expansion — which were never fixed.

## Decision

Deprecate and remove swain-dispatch entirely:

1. **Skill folder deleted** (`skills/swain-dispatch/`)
2. **GitHub Actions workflow deleted** (`.github/workflows/agent-dispatch.yml`)
3. **Router and help references removed** (swain router table, quick-ref)
4. **Doctor cleanup registered** (`legacy-skills.json` retired map) so swain-doctor will auto-delete the skill folder if a future swain-update reinstalls it
5. **Bug-fix spec abandoned** ([SPEC-074](../../spec/Abandoned/(SPEC-074)-Fix-Dispatch-Functional-Bugs/(SPEC-074)-Fix-Dispatch-Functional-Bugs.md))

The original implementation specs ([SPEC-025](../../spec/Complete/(SPEC-025)-Swain-Dispatch-Skill/(SPEC-025)-Swain-Dispatch-Skill.md), [SPEC-029](../../spec/Complete/(SPEC-029)-Swain-Dispatch-Prerequisites-And-Invocation-Docs/(SPEC-029)-Swain-Dispatch-Prerequisites-And-Invocation-Docs.md)) remain in Complete as historical record.

## Alternatives Considered

**Keep the skill with a "bring your own API key" model.** Rejected because the project's primary operator uses Max/Pro, and maintaining a skill that requires a separate billing arrangement creates ongoing confusion and maintenance burden for zero current utility.

**Disable but preserve the skill code.** Rejected because the skill had unfixed functional bugs, and dead code attracts maintenance questions. The git history preserves the implementation if needed.

**Port to a non-API execution model (e.g., local background agents).** Deferred — in-session parallel agents (via the `dispatching-parallel-agents` skill) cover the primary use case. A future dispatch model that works with Max/Pro credentials could supersede this ADR.

## Consequences

**Positive:**
- Eliminates a non-functional skill from the installed skill set, reducing routing noise and confusion
- Removes the GitHub Actions workflow that would fail without an API key
- Closes an open bug-fix spec that would never be implemented

**Accepted downsides:**
- No background/asynchronous agent dispatch capability — all agent work must happen in-session
- If Anthropic later supports non-API-key authentication for GitHub Actions (or similar CI/CD runners), the dispatch concept will need to be rebuilt from scratch

**Revisit conditions:**
- Anthropic releases a mechanism for Max/Pro credentials to authenticate `claude-code-action` in CI/CD
- A non-GitHub-Actions dispatch model emerges that doesn't require per-token API billing

This ADR should be **superseded** (not retired) when dispatch capability is restored, since the replacement will likely take a different architectural approach.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | -- | Decision recorded after skill removal |
