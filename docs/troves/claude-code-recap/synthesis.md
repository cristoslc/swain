# Claude Code /recap — Synthesis

## Key Findings

`/recap` was introduced in **v2.1.108 on April 14, 2026**. It generates a context
summary when you return to an active session after stepping away. The underlying
mechanism is called "away summary" (`CLAUDE_CODE_ENABLE_AWAY_SUMMARY`). You can
also invoke it manually with `/recap` or configure it in `/config`.

### What It Does

When you leave an active Claude Code session and come back, `/recap` gives you a
"where were we?" summary — the conversation context, current task state, and key
decisions made before you stepped away. It reorients you without requiring you to
scroll back through the full session history.

It is distinct from every other memory feature in Claude Code:

| Feature | Trigger | Scope | Storage |
|---------|---------|-------|---------|
| `/compact` | Context fullness | In-session compression | Replaces history |
| Session Memory | Automatic, background | Cross-session (days) | `~/.claude/projects/...` |
| Auto memory | Automatic | Persistent project notes | `MEMORY.md` |
| **`/recap`** | On return or `/recap` | In-session (stepped away) | Ephemeral |

### Configuration

Three ways to control `/recap`:
1. **`/config`** — toggle the feature on/off in settings.
2. **`/recap`** — invoke manually at any time.
3. **`CLAUDE_CODE_ENABLE_AWAY_SUMMARY`** — env var to force it when telemetry
   is disabled (telemetry is normally how Claude Code detects the "away" state).

### Availability

The release notes do not restrict `/recap` by plan. The `CLAUDE_CODE_ENABLE_AWAY_SUMMARY`
env var and telemetry note suggest the auto-trigger relies on usage telemetry to detect
inactivity periods. Users with telemetry disabled must force it via the env var or run
`/recap` manually.

## Context: The Session-Continuity Trajectory

`/recap` did not appear in isolation. A six-month trajectory of session-continuity
improvements preceded it:

1. **v2.0.64 (late 2025)** — Session Memory background summaries introduced.
2. **v2.1.30–31 (Feb 2026)** — Session Memory becomes visible ("Recalled/Wrote
   memories" messages).
3. **v2.1.69 (Mar 5, 2026)** — Compaction preamble "recap" removed. Post-compaction
   resume no longer auto-emits a context summary.
4. **v2.1.87 (Mar 29, 2026)** — `/resume` picker shows most recent prompt (better
   re-orientation on resume).
5. **v2.1.108 (Apr 14, 2026)** — `/recap` launched.

The v2.1.69 change (removing the compaction preamble) likely informed the `/recap`
design: the team removed the implicit, always-on preamble recap and replaced it with
an explicit, on-demand (and return-triggered) one.

## Points of Agreement

- `/recap` fills a gap that neither Session Memory nor `/compact` covered: the
  "stepped away from an active session" case where context is still live but
  attention has drifted.
- The `AWAY_SUMMARY` name confirms the triggering condition is time-based absence
  from an active session, not a content-driven threshold.

## Points of Disagreement / Uncertainty

- Exact "away" threshold is not documented. It is unclear whether the trigger is
  time-based (e.g., 30 minutes of inactivity), terminal-focus-based, or telemetry-
  derived heuristic.
- Whether `/recap` produces a summary via the model (like `/compact`) or reads from
  Session Memory's pre-written summaries is not confirmed in public documentation.

## Gaps

- No official docs page for `/recap` yet (v2.1.108 landed the same day as this
  trove was built). The only source is the changelog entry.
- No community usage reports yet — too new.
- No documentation of the auto-trigger threshold or telemetry dependency.
- Relationship to `swain-session` / `swain-helm` workflows is unexplored. The
  swain-session greeting already provides a bookmark ("Resuming session — Last
  time: X"). `/recap` may offer finer-grained within-session re-orientation on top
  of that.
