# Claude Code /recap — Synthesis

## Key Findings

`/recap` was introduced in **v2.1.108 on April 14, 2026**. It generates a
context summary when you return to an active session after stepping away. The
underlying mechanism is called "away summary" (`CLAUDE_CODE_ENABLE_AWAY_SUMMARY`).
You can also invoke it manually with `/recap` or configure it in `/config`.

### What It Does

When you leave an active Claude Code session and come back, `/recap` gives you
a "where were we?" summary — the conversation context, current task state, and
key decisions made before you stepped away. It reorients you without requiring
you to scroll back through the full session history.

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
   is disabled.

### Availability

The release notes do not restrict `/recap` by plan. The
`CLAUDE_CODE_ENABLE_AWAY_SUMMARY` env var and telemetry note suggest the
auto-trigger relies on usage telemetry to detect inactivity. Users with
telemetry disabled must force it via the env var or run `/recap` manually.

---

## How /recap Is Generated (Resolved)

Earlier versions of this synthesis flagged the generation mechanism as unknown.
This is now resolved.

**`/recap` reads from Session Memory — it does not run a fresh model call.**

Evidence:
- The Piebald-AI system prompts repo (which extracts prompts directly from
  Claude Code's compiled source) shows **no new prompt was added in v2.1.108**
  for recap or away-summary. The existing prompts are
  `agent-prompt-conversation-summarization` and
  `agent-prompt-recent-message-summarization` (both since v2.1.84).
- ClaudeFast's context management guide confirms: "Compaction is fast because
  Claude maintains a continuous session memory in the background, so compaction
  loads that summary into a fresh context rather than re-summarizing."
- `/compact` and `/recap` share the same data source: the `summary.md` file
  maintained continuously at
  `~/.claude/projects/<hash>/<session-id>/session_memory/`.

The architecture:
- **Session Memory agent** runs in the background, updating `summary.md` as
  you work (sections: Current State, Task Specification, Files and Functions,
  Workflow, Errors & Corrections, Learnings, Key Results, Worklog).
- **`/compact`** reads `summary.md` → replaces conversation history with it.
- **`/recap`** reads `summary.md` → injects it as a briefing alongside the
  existing history (no replacement).
- The `AWAY_SUMMARY` mechanism detects the "away" state (via telemetry) and
  triggers the injection automatically on return.

### Away threshold (still unresolved)

The exact inactivity duration that triggers auto-recap is not documented. The
trigger is telemetry-derived (usage data, not a fixed timer). No community
reports exist yet — `/recap` is too new.

---

## Context: The Session-Continuity Trajectory

`/recap` did not appear in isolation. A six-month trajectory of
session-continuity improvements preceded it:

1. **v2.0.64 (late 2025)** — Session Memory background summaries introduced.
2. **v2.1.30–31 (Feb 2026)** — Session Memory becomes visible ("Recalled/Wrote
   memories" messages).
3. **v2.1.69 (Mar 5, 2026)** — Compaction preamble "recap" removed.
   Post-compaction resume no longer auto-emits a context summary.
4. **v2.1.84** — `conversation-summarization` and `recent-message-summarization`
   agent prompts exist in compiled source (baseline for recap infrastructure).
5. **v2.1.87 (Mar 29, 2026)** — `/resume` picker shows most recent prompt
   (better re-orientation on resume).
6. **v2.1.108 (Apr 14, 2026)** — `/recap` launched as a UX wrapper over the
   existing session memory + summarization infrastructure.

The v2.1.69 change (removing the compaction preamble) likely informed the
`/recap` design: the team removed the implicit, always-on preamble recap and
replaced it with an explicit, on-demand (and return-triggered) one.

---

## Points of Agreement

- `/recap` fills a gap that neither Session Memory nor `/compact` covered: the
  "stepped away from an active session" case where context is still live but
  attention has drifted.
- `/recap` is architecturally a read of pre-written session memory, not a
  fresh generation step. This makes it fast and low-cost.
- The `AWAY_SUMMARY` name confirms the triggering condition is absence from an
  active session, not a content-driven threshold.

## Points of Disagreement / Uncertainty

- Exact "away" threshold is not documented and may be a telemetry heuristic
  rather than a fixed duration.
- Whether "Current State" in the session memory template is sufficient for
  reorientation, or whether `/recap` injects the full `summary.md`, is not
  confirmed. The full template has 9 sections; a targeted read of just
  "Current State" would be lighter.

---

## Implications for EPIC-022 (Postflight Summaries)

`/recap` and EPIC-022's postflight address adjacent but distinct cases:

| | /recap | EPIC-022 postflight |
|--|--------|---------------------|
| **Trigger** | Operator steps away from active session | A swain skill completes |
| **Who invokes** | Claude Code (auto) or operator (manual) | The completing swain skill |
| **Data source** | Session Memory (`summary.md`) | The artifact just worked on |
| **Output framing** | "Where were we?" | "What just happened + what's next?" |
| **Context effect** | Injects alongside live history | Lightweight terminal output only |
| **Swain-aware?** | No — unaware of artifacts/tickets | Yes — reads artifact IDs, goals |

These are not the same feature. `/recap` handles re-orientation after absence.
EPIC-022 handles context recovery after a tool-mediated task completes — the
operator was present but deep in a skill, and lost sight of the project picture.

The recommendation for EPIC-022: **narrow scope, do not abandon**. Claude Code
now owns the "stepped away" case. EPIC-022 should explicitly position itself as
the skill-completion case and lean into swain-specific domain context (artifact
titles, goals, recommendations) that `/recap`'s generic session memory cannot
provide.

Specifically: EPIC-022's postflight has value that `/recap` cannot replicate
because it reads the artifact's goal, uses the swain recommendation engine, and
speaks in project terms (SPEC-042 implemented, EPIC-017 unblocked) rather than
file and code terms (session memory's vocabulary).
