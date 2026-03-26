---
title: "Retro: Trove misrouting — standalone trove created instead of extending existing"
artifact: RETRO-2026-03-25-trove-misrouting
track: standing
status: Active
created: 2026-03-25
last-updated: 2026-03-25
scope: "swain-search invocation for marciopuga/cog repo"
period: "2026-03-25"
linked-artifacts:
  - SPIKE-044
  - EPIC-044
---

# Retro: Trove misrouting

## Summary

User invoked `/swain-search https://github.com/marciopuga/cog`. The agent created a standalone `cog-cognitive-architecture` trove instead of extending the existing `agent-memory-systems` trove. User caught the error. Three extra commits were needed to fix it: move the source into the correct trove, rewrite the synthesis, and delete the standalone trove.

## Sequence of events

1. `/swain-search` invoked with a GitHub repo URL
2. Prior art check ran `grep -rl "cog" docs/troves/*/manifest.yaml` — matched `cognee` in `agent-memory-systems` but agent dismissed it as unrelated
3. Agent never searched by semantic topic (tags like `agent-memory`, `memory-architecture`, `claude-code`)
4. Standalone `cog-cognitive-architecture` trove created, committed, pushed (`ea445b2`)
5. Agent added the standalone trove to SPIKE-044's evidence pool (`45e3031`)
6. User asked "anything worth artifacting?" — agent correctly identified SPIKE-044 as the home
7. User asked why the source wasn't put in the `agent-memory-systems` trove — agent agreed it was wrong
8. Fix: moved source to `agent-memory-systems`, rewrote synthesis, rewrote SPIKE-044, deleted standalone trove (`4fc8ffc`)

Total waste: 3 unnecessary commits (`ea445b2`, `8bbf62d`, `45e3031`), ~20 minutes of rework.

## Reflection

### Root cause: literal keyword search instead of semantic topic matching

The prior art check in the skill instructions says to search existing troves by keyword. The agent searched for "cog" (the repo name) and "marciopuga" (the author). Neither matched. But the *topic* — "agent memory system for Claude Code" — is exactly what `agent-memory-systems` covers.

The skill's prior art check uses `grep -rl "<keyword>"` which only matches literal strings. This works when the new source shares vocabulary with existing troves (e.g., adding a WebSocket article to a `websocket-vs-sse` trove). It fails when the new source uses different vocabulary for the same concept (e.g., "Cog" vs. "agent memory systems").

### What would have caught this

1. **Search by topic tags, not just source name.** After the literal grep, search existing trove tags: `grep -l "agent-memory\|memory-architecture\|claude-code" docs/troves/*/manifest.yaml`. This would have immediately surfaced `agent-memory-systems`.

2. **Read the source before choosing a trove.** The agent fetched the repo, read the full contents, understood it was a memory system — and *still* created a standalone trove. The classification step ("what is this source about? does an existing trove cover that topic?") was skipped. Understanding the source's topic should happen before the trove create/extend decision, not after.

3. **Explicit "does this belong in an existing trove?" gate.** The skill's mode detection table has Create vs. Extend, but the decision is implicit. A forced checkpoint — "I identified these existing troves as potentially relevant: X, Y. None match / extending X" — would make the decision visible and reviewable.

### The deeper pattern

This is a **name-vs-concept confusion** failure. The agent anchored on the source's *name* ("cog") when routing, instead of its *meaning* ("agent memory system"). This same failure mode could recur any time a source uses novel vocabulary for a known concept.

The fix isn't just better grep patterns — it's a two-phase prior art check: (1) literal keyword match on source name/URL, then (2) semantic topic match against trove tags and synthesis summaries. Phase 2 is what was missing.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_trove_organization.md | feedback | Extend topical troves, don't create standalone ones for individual sources |
