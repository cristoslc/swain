---
title: "Telemetry Aggregator and Summary Generation"
artifact: SPEC-246
type: feature
status: Proposed
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
parent-epic: EPIC-057
linked-artifacts:
  - DESIGN-015
  - EPIC-057
artifact-refs: []
depends-on-artifacts:
  - SPEC-245
swain-do: required
---

# Telemetry Aggregator and Summary Generation

## Context
Implement the daily aggregation logic that converts raw JSONL events into summary statistics per DESIGN-015. This is the `aggregator.py` component.

## Acceptance Criteria

### Aggregator Script
- [ ] Location: `skills/swain-telemetry/scripts/aggregator.py`
- [ ] Invocation: `python3 aggregator.py --date YYYY-MM-DD` (default: today)
- [ ] Reads: `.swain/telemetry/events/YYYY-MM-DD.jsonl`
- [ ] Writes: `.swain/telemetry/events/YYYY-MM-DD-summary.json`

### Summary Schema
Output must match this exact schema:
```json
{
  "period": "YYYY-MM-DD/YYYY-MM-DD",
  "swain_version": "0.27.1",
  "totals": {
    "skill_invoked": 142,
    "artifact_created": 23,
    "session_started": 8
  },
  "by_skill": {
    "swain-design": 31,
    "swain-session": 54
  },
  "by_artifact_type": {
    "SPEC": 14,
    "EPIC": 3
  },
  "session_stats": {
    "total_sessions": 8,
    "avg_duration_minutes": 47,
    "worktree_sessions": 5
  }
}
```

### Aggregation Rules
- [ ] `totals`: Count of each event type
- [ ] `by_skill`: Count grouped by `data.skill_name` (from `skill_invoked` events)
- [ ] `by_artifact_type`: Count grouped by `data.artifact_type` (from `artifact_created` and `artifact_transitioned`)
- [ ] `session_stats`:
  - `total_sessions`: Count of `session_started` events
  - `avg_duration_minutes`: Average of `data.duration_minutes` from `session_closed` (bucket to nearest 5)
  - `worktree_sessions`: Count where `data.worktree_used: true`

### Duration Buckets
For privacy, bucket durations to nearest 5 minutes:
- 0-2 min → 0
- 3-7 min → 5
- 8-12 min → 10
- etc.

### Error Handling
- [ ] Missing input file: exit 0, create empty summary
- [ ] Malformed JSONL: skip line, log warning to stderr
- [ ] Missing fields in event: use defaults (0 for counts)
- [ ] No events: create summary with all zeros

### Privacy Enforcement
- [ ] No identifiers in output
- [ ] Duration bucketing applied
- [ ] Minimum count threshold: if count < 3 for a skill, group as "other" (prevents fingerprinting)

## Implementation Notes

**Aggregator logic:**
```python
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def aggregate_events(date_str: str):
    event_dir = Path.home() / ".swain" / "telemetry" / "events"
    input_file = event_dir / f"{date_str}.jsonl"
    output_file = event_dir / f"{date_str}-summary.json"
    
    totals = defaultdict(int)
    by_skill = defaultdict(int)
    by_artifact_type = defaultdict(int)
    session_durations = []
    worktree_sessions = 0
    
    if input_file.exists():
        for line in input_file.read_text().splitlines():
            try:
                event = json.loads(line)
                event_type = event.get("event", "")
                data = event.get("data", {})
                
                totals[event_type] += 1
                
                if event_type == "skill_invoked":
                    skill = data.get("skill_name", "unknown")
                    by_skill[skill] += 1
                
                elif event_type in ["artifact_created", "artifact_transitioned"]:
                    artifact_type = data.get("artifact_type", "unknown")
                    by_artifact_type[artifact_type] += 1
                
                elif event_type == "session_closed":
                    duration = data.get("duration_minutes", 0)
                    session_durations.append(duration)
                
                elif event_type == "session_started":
                    if data.get("worktree_used", False):
                        worktree_sessions += 1
                        
            except json.JSONDecodeError:
                continue
    
    # Apply privacy threshold to skills
    by_skill_filtered = {}
    other_count = 0
    for skill, count in by_skill.items():
        if count >= 3:
            by_skill_filtered[skill] = count
        else:
            other_count += count
    if other_count > 0:
        by_skill_filtered["other"] = other_count
    
    # Calculate session stats
    avg_duration = 0
    if session_durations:
        avg_duration = sum(session_durations) // len(session_durations)
        # Bucket to nearest 5
        avg_duration = round(avg_duration / 5) * 5
    
    summary = {
        "period": f"{date_str}/{date_str}",
        "swain_version": "0.27.1",  # TODO: get from version file
        "totals": dict(totals),
        "by_skill": by_skill_filtered,
        "by_artifact_type": dict(by_artifact_type),
        "session_stats": {
            "total_sessions": totals.get("session_started", 0),
            "avg_duration_minutes": avg_duration,
            "worktree_sessions": worktree_sessions
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
```

## Dependencies
- EPIC-057 (parent epic)
- SPEC-245 (event emission)

## Test Plan
- [ ] Aggregator runs successfully
- [ ] Summary matches expected schema
- [ ] Counts are accurate
- [ ] Duration bucketing works
- [ ] Privacy threshold applied to skills
- [ ] Handles missing input gracefully
- [ ] Handles malformed JSONL gracefully
- [ ] No identifiers in output

## Linked Design Intent
From DESIGN-015:
- **Goal**: Aggregate by default, auditable format
- **Principle**: No personal data, local-only processing
- **Data Format**: Summary JSON schema as specified
