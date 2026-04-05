---
title: "Telemetry Configuration Management"
artifact: SPEC-244
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
depends-on-artifacts: []
swain-do: required
---

# Telemetry Configuration Management

## Context
Implement the configuration layer for the telemetry system per DESIGN-015. This SPEC covers the config file management and CLI commands for enabling/disabling telemetry.

## Acceptance Criteria

### Config File Management
- [ ] Config file location: `.swain/telemetry/config.json`
- [ ] Schema: `{"enabled": boolean, "endpoint": string|null}`
- [ ] Default state: `enabled: false` (never auto-enabled)
- [ ] Created only on explicit `swain telemetry enable` command
- [ ] Config read before each event emission (no caching)

### CLI Commands
- [ ] `swain telemetry enable [--endpoint URL]`
  - Creates config with `enabled: true`
  - Optional `--endpoint` sets the export URL
  - Prints confirmation message
- [ ] `swain telemetry disable`
  - Sets `enabled: false`
  - Preserves existing log files
  - Prints confirmation message
- [ ] `swain telemetry status`
  - Shows enabled/disabled state
  - Shows configured endpoint (if any)
  - Shows event counts for today
  - Shows last export timestamp (if any)

### Privacy Safeguards
- [ ] No identifiers in config (user, project, session)
- [ ] Endpoint validation (must be valid URL if provided)
- [ ] Config file permissions: readable only by owner (0600)

## Implementation Notes

**Directory structure:**
```
.swain/
  telemetry/
    config.json
    events/
```

**Config creation logic:**
```python
import json
import os
from pathlib import Path

def enable_telemetry(endpoint=None):
    config_dir = Path.home() / ".swain" / "telemetry"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "enabled": True,
        "endpoint": endpoint
    }
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set permissions to 0600
    os.chmod(config_file, 0o600)
```

**Status command output:**
```
Telemetry Status
----------------
Enabled: false
Endpoint: (not configured)
Events today: 0
Last export: (never)
```

## Dependencies
- EPIC-057 (parent epic)

## Test Plan
- [ ] Config file created with correct schema
- [ ] Permissions set to 0600
- [ ] Enable without endpoint works
- [ ] Enable with endpoint works
- [ ] Disable preserves logs
- [ ] Status shows correct counts
- [ ] Invalid URL rejected

## Linked Design Intent
From DESIGN-015:
- **Goal**: Opt-in, local-first, operator-controlled
- **Constraint**: No identifiers, single toggle disables all
- **Non-goal**: Auto-enable, cloud submission without consent
