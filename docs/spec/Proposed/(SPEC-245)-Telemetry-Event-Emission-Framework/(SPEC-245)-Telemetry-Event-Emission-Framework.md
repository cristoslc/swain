---
title: "Telemetry Event Emission Framework"
artifact: SPEC-245
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
  - SPEC-244
swain-do: required
---

# Telemetry Event Emission Framework

## Context
Implement the event emission framework that skills use to log telemetry events. This SPEC covers the emitter library and event schemas per DESIGN-015.

## Acceptance Criteria

### Event Emitter Library
- [ ] Location: `skills/swain-telemetry/scripts/emit-telemetry.sh` (or `.py`)
- [ ] Function signature: `emit_event(event_type, data_payload)`
- [ ] Config check before emission (skip if disabled)
- [ ] Graceful degradation: no-op if config missing or malformed
- [ ] Error handling: log to stderr, never block skill execution

### Event Types and Schemas
Implement these 8 event types with exact schemas:

| Event | When | `data` payload |
|-------|------|----------------|
| `skill_invoked` | A skill is loaded | `{"skill_name": "swain-design", "trigger_word": "design"}` |
| `artifact_created` | New artifact file written | `{"artifact_type": "SPEC", "parent_type": "EPIC", "parent_id": "EPIC-054"}` |
| `artifact_transitioned` | Artifact moves lifecycle phase | `{"artifact_type": "SPEC", "artifact_id": "SPEC-123", "from_phase": "Proposed", "to_phase": "Active"}` |
| `session_started` | New session begins | `{"launcher": "swain-init", "purpose_set": "implementation"}` |
| `session_closed` | Session ends | `{"duration_minutes": 47, "worktree_used": true}` |
| `worktree_created` | Worktree spawned | `{"trigger": "auto"}` |
| `spec_completed` | SPEC reaches Complete | `{"has_tests": true, "has_verification": true}` |
| `command_run` | Shell command executed via swain | `{"command_category": "sync"}` |

**Command categories:** `sync`, `session`, `doctor`, `test`, `security`, `other`

### Event Log Format
- [ ] File format: JSONL (one JSON per line)
- [ ] File naming: `YYYY-MM-DD.jsonl`
- [ ] Location: `.swain/telemetry/events/`
- [ ] Append-only: never modify existing lines
- [ ] Timestamp: ISO-8601 with timezone

### Integration Points
Integrate emission into these skills:
- [ ] `swain-session`: session_started, session_closed
- [ ] `swain-design`: artifact_created, artifact_transitioned
- [ ] `swain-do`: spec_completed
- [ ] All skills: skill_invoked
- [ ] `swain-worktree`: worktree_created

### Privacy Enforcement
- [ ] No file paths in any event
- [ ] No artifact names (only types and IDs)
- [ ] No user/project identifiers
- [ ] No skill outputs or error details
- [ ] No code snippets or prompts

## Implementation Notes

**Event emitter (Python example):**
```python
import json
from pathlib import Path
from datetime import datetime

def emit_event(event_type: str, data: dict):
    config_path = Path.home() / ".swain" / "telemetry" / "config.json"
    
    # Check if enabled
    if not config_path.exists():
        return
    
    try:
        config = json.loads(config_path.read_text())
        if not config.get("enabled", False):
            return
    except (json.JSONDecodeError, IOError):
        return
    
    # Write event
    event_dir = Path.home() / ".swain" / "telemetry" / "events"
    event_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    event_file = event_dir / f"{today}.jsonl"
    
    event = {
        "ts": datetime.now().isoformat(),
        "event": event_type,
        "data": data
    }
    
    with open(event_file, 'a') as f:
        f.write(json.dumps(event) + '\n')
```

**Shell wrapper (for bash skills):**
```bash
emit_telemetry() {
    local event_type="$1"
    local data_payload="$2"
    python3 -c "
from telemetry_emitter import emit_event
emit_event('$event_type', $data_payload)
" 2>/dev/null || true
}
```

## Dependencies
- EPIC-057 (parent epic)
- SPEC-244 (config management)

## Test Plan
- [ ] Event emitted when enabled
- [ ] No event when disabled
- [ ] No event when config missing
- [ ] JSONL format correct
- [ ] Timestamps valid ISO-8601
- [ ] All 8 event types work
- [ ] No PII in any event payload
- [ ] Errors don't block skill execution

## Linked Design Intent
From DESIGN-015:
- **Goal**: Coarse-grained events, auditable JSONL format
- **Principle**: No personal data, aggregate by default
- **Constraint**: Local-only submission
