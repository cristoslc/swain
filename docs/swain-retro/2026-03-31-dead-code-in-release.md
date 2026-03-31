---
title: "Retro: Dead Code Ships With Passing Tests"
artifact: RETRO-2026-03-31-dead-code-in-release
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "Aborted v0.25.0-alpha release after discovering EPIC-049 scripts were never invoked"
period: "2026-03-31"
linked-artifacts:
  - EPIC-049
  - SPEC-199
  - SPEC-200
  - SPEC-205
---

# Retro: Dead Code Ships With Passing Tests

## Summary

A routine release attempt (v0.25.0-alpha) was aborted mid-ceremony when the operator asked whether the progress-log script was actually invoked by any skill. It wasn't. Two scripts — `swain-session-digest.sh` and `swain-progress-log.sh` — had been implemented under [SPEC-199](../spec/Active/(SPEC-199)-Session-Digest-Auto-Generation/(SPEC-199)-Session-Digest-Auto-Generation.md) and [SPEC-200](../spec/Active/(SPEC-200)-Progress-Log-and-Synthesis/(SPEC-200)-Progress-Log-and-Synthesis.md), passed unit tests, got merged to trunk, and were staged for a changelog headline. But no skill called them. They were dead code with a test suite.

The operator caught the gap by asking "did you do an integration test?" after the release was already tagged. The release was aborted (tag deleted, trunk and release branch reverted), a bug spec was created ([SPEC-205](../spec/Active/(SPEC-205)-Wire-Progress-Log-Into-Session-Close/(SPEC-205)-Wire-Progress-Log-Into-Session-Close.md)), and the fix was implemented and merged in the same session.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-205](../spec/Active/(SPEC-205)-Wire-Progress-Log-Into-Session-Close/(SPEC-205)-Wire-Progress-Log-Into-Session-Close.md) | Wire Progress Log Into Session Close | Implemented and merged |
| v0.25.0-alpha | Release | Aborted — changelog overstated what shipped |

## Reflection

### What went well

The release process itself surfaced the problem. The operator's instinct to ask "does this actually work?" during release review caught a gap that unit tests, specwatch scans, and multiple prior commits missed. Once caught, the fix was small — a skill file edit adding two script calls to the session close section. The full cycle from discovery to merged fix took under an hour.

The abort was clean. Tag deleted, trunk reset, release branch reverted, no artifacts pushed to remote. The release skill's multi-step ceremony (tag on trunk, squash-merge to release) made the rollback straightforward because nothing had been pushed yet.

### What was surprising

Four specs ([SPEC-199](../spec/Active/(SPEC-199)-Session-Digest-Auto-Generation/(SPEC-199)-Session-Digest-Auto-Generation.md) through SPEC-202) were implemented, tested, and merged across multiple sessions without anyone verifying that the scripts were actually called at runtime. Each spec's acceptance criteria described the behavior ("when the session closes, then a digest is generated") but verification was done against the script in isolation, not the end-to-end path. The session close procedure in swain-session SKILL.md was never updated.

[SPEC-200](../spec/Active/(SPEC-200)-Progress-Log-and-Synthesis/(SPEC-200)-Progress-Log-and-Synthesis.md) explicitly said "swain-retro reads artifacts_touched and appends a dated entry" — but swain-retro runs at EPIC completion, not every session close. The spec described the wrong caller, and implementation followed the spec literally (building the script) without questioning the integration point.

### What would change

The root cause is that SPEC acceptance criteria described script behavior ("given X, when the script runs, then Y") but not integration behavior ("given a session close, when the operator says done, then the digest runs"). The scripts were correct — they just weren't reachable from any user-facing workflow. A "who calls this?" check during spec completion would have caught it.

The changelog wrote about the scripts as shipped features. The release skill doesn't verify that claimed features are reachable from user-facing workflows — it reads commit messages and classifies them. A release checklist item like "for each feature heading, trace the invocation path from operator action to script" would prevent overstated changelogs.

### Patterns observed

This is the "tested but not wired" anti-pattern: code that passes its own tests but has no caller. It's a decomposition failure — when work is split into specs (digest script, progress-log script, context utility, display integration), the integration wiring between them falls through the cracks unless a spec explicitly owns it.

Prior retros have flagged related patterns. The overnight autonomous sweep retro (2026-03-22) noted that dispatched agents complete specs in isolation without verifying cross-spec integration. This is the same shape: each spec was "done" individually, but the system-level behavior never worked.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Integration wiring spec required for multi-script epics | SPEC candidate | When an EPIC decomposes into scripts that form a pipeline, one spec must own the end-to-end wiring and verify the invocation path from user action to script execution |
| Release changelog verification | SPEC candidate | swain-release should verify that feature headlines trace to a reachable invocation path, not just a merged commit |
| SPEC completion gate: "who calls this?" | SPEC candidate | Before transitioning a script-producing SPEC to Complete, verify the script is invoked by at least one skill or hook — not just tested in isolation |
