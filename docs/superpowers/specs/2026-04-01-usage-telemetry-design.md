# Usage Logging and Telemetry — Design

**Date:** 2026-04-01
**Status:** Draft

## Intent

Track aggregate feature utilization in swain to inform improvement decisions — not to monitor individuals or capture private data. All collection is **opt-in**, anonymous, and local-first.

## Principles

1. **No personal data** — no user ID, no project names, no file paths, no code content
2. **Aggregate by default** — events describe swain behavior, not operator behavior
3. **Local-only submission** — events land in a local log first; operator controls export
4. **Easy opt-out** — one flag disables all collection permanently
5. **Auditable** — every event is human-readable JSONL; operator can inspect before submitting

## Events

Events are coarse-grained feature signals. Each event includes:
- `ts` — ISO timestamp
- `event` — event name (enum)
- `data` — event-specific payload (always coarse categories, never paths or names)

**Proposed event types:**

| Event | When | `data` payload |
|-------|------|----------------|
| `skill_invoked` | A skill is loaded | `skill_name`, `trigger_word` |
| `artifact_created` | New artifact file written | `artifact_type`, `parent_type`, `parent_id` |
| `artifact_transitioned` | Artifact moves lifecycle phase | `artifact_type`, `artifact_id`, `from_phase`, `to_phase` |
| `session_started` | New session begins | `launcher`, `purpose_set` |
| `session_closed` | Session ends | `duration_minutes` bucket, `worktree_used` |
| `worktree_created` | Worktree spawned | `trigger` (manual/auto) |
| `spec_completed` | SPEC reaches Complete | `has_tests`, `has_verification` |
| `command_run` | Shell command executed via swain | `command_category` (sync/session/doctor/test/security/other) |

**Excluded by default:** file paths, artifact names, user/project identifiers, skill outputs, error details, user prompts, code snippets.

## Architecture

```
.swain/
  telemetry/
    config.json          # { enabled: false, endpoint: null }
    events/
      YYYY-MM-DD.jsonl   # One file per day, append-only
    aggregator.py        # Local-only: summarizes daily events → aggregate stats
    exporter.sh          # Operator-controlled: ship aggregated JSON to endpoint
```

- **`config.json`** — single toggle + endpoint URL. Defaults `enabled: false`. Created on first opt-in. No identifiers stored.
- **`events/*.jsonl`** — raw events, never leaves machine unless operator runs exporter.
- **`aggregator.py`** — produces a `YYYY-MM-DD-summary.json` with counts per event type. Run locally.
- **`exporter.sh`** — reads summaries, POSTs to operator-configured endpoint. Never sends raw events.

## Opt-in Flow

```bash
# Operator explicitly enables:
swain telemetry enable [--endpoint https://my-collector.example.com/ingest]

# Check status:
swain telemetry status    # shows enabled/disabled, event counts, last export

# Export (operator-initiated):
swain telemetry export   # ships summaries to configured endpoint

# Disable:
swain telemetry disable  # sets enabled: false, stops collection, preserves log files
```

Collection stops immediately on `disable`. Historical logs remain for operator inspection.

## Data Format (Exported Summary)

```json
{
  "period": "2026-04-01/2026-04-07",
  "swain_version": "0.27.1",
  "totals": {
    "skill_invoked": 142,
    "artifact_created": 23,
    "session_started": 8
  },
  "by_skill": {
    "swain-design": 31,
    "swain-session": 54,
    "swain-do": 28
  },
  "by_artifact_type": {
    "SPEC": 14,
    "EPIC": 3,
    "SPIKE": 4,
    "ADR": 2
  },
  "session_stats": {
    "total_sessions": 8,
    "avg_duration_minutes": 47,
    "worktree_sessions": 5
  }
}
```

The endpoint sees only aggregate counts — no identifiers, no paths, nothing traceable to a user or project.

## Privacy Safeguards

- No user, project, or session identifiers — export contains only aggregate counts
- No IP address collection (endpoint receives only the summary JSON)
- No artifact content, names, or paths
- Operator can inspect `events/*.jsonl` at any time
- All processing is local until operator explicitly runs `export`

## OpenTelemetry Alignment

Events map cleanly to OTel metrics and traces:
- Skill invocations → counter metric
- Session duration → histogram
- Artifact lifecycle → span events

The `exporter.sh` can output OTLP-compatible JSON for easy ingestion into existing OTel pipelines. The existing trove at `docs/troves/opentelemetry` provides sufficient reference.

## Deferred: Endpoint Backend

The endpoint is out of scope for this design. Operators can use any HTTP POST receiver. A future spec may define a lightweight shared aggregator service, but initial rollout is self-hosted or third-party only.

## Component Checklist

- [ ] `swain telemetry enable` — creates config, sets enabled
- [ ] `swain telemetry disable` — clears enabled flag
- [ ] `swain telemetry status` — reads config, shows counts
- [ ] `swain telemetry export` — runs exporter
- [ ] Event emission hooks in skills (swain-session, swain-design, swain-do)
- [ ] `aggregator.py` — daily summary generation
- [ ] `exporter.sh` — HTTP POST of summaries
- [ ] Opt-in prompt during swain-init (ask operator, don't enable by default)
- [ ] Privacy manifest entry
