---
title: "Telemetry Export Mechanism"
artifact: SPEC-247
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
  - SPEC-246
swain-do: required
---

# Telemetry Export Mechanism

## Context
Implement the export mechanism that allows operators to send aggregated telemetry summaries to external endpoints per DESIGN-015. This SPEC covers `exporter.sh` and the `swain telemetry export` command.

## Acceptance Criteria

### Export Command
- [ ] Command: `swain telemetry export [--date-range START END]`
- [ ] Default: export all unexported summaries since last export
- [ ] Optional: export specific date range
- [ ] Reads config for endpoint URL
- [ ] Fails gracefully if endpoint not configured

### Export Logic
- [ ] Reads summaries from `.swain/telemetry/events/YYYY-MM-DD-summary.json`
- [ ] Tracks last export timestamp in config
- [ ] Only exports summaries newer than last export
- [ ] Batches multiple summaries into single POST
- [ ] Content-Type: `application/json`

### HTTP POST Request
```json
{
  "summaries": [
    { /* summary JSON for date 1 */ },
    { /* summary JSON for date 2 */ }
  ],
  "exported_at": "ISO-8601 timestamp",
  "swain_version": "0.27.1"
}
```

### Response Handling
- [ ] Success (2xx): log success, update last export timestamp
- [ ] Client error (4xx): log error, don't retry
- [ ] Server error (5xx): log error, retry on next export
- [ ] Timeout: log error, retry on next export (30s timeout)

### Export History
- [ ] Log export attempts to `.swain/telemetry/export-log.jsonl`
- [ ] Each entry: `{ts, status, endpoint, summary_count, error?}`
- [ ] Retain last 100 entries (rotate older)

### Privacy Verification
- [ ] Verify no identifiers in summaries before sending
- [ ] Dry-run mode: `swain telemetry export --dry-run` shows what would be sent
- [ ] Operator confirmation prompt before first export to new endpoint

### OTel Compatibility
- [ ] Export format compatible with OTLP JSON encoding
- [ ] Field names align with OTel metrics conventions
- [ ] Future-proof for OTLP exporter addition

## Implementation Notes

**Exporter script (Python):**
```python
import json
import requests
from pathlib import Path
from datetime import datetime

def export_telemetry(start_date=None, end_date=None, dry_run=False):
    config_path = Path.home() / ".swain" / "telemetry" / "config.json"
    config = json.loads(config_path.read_text())
    
    endpoint = config.get("endpoint")
    if not endpoint:
        print("Error: No endpoint configured. Run: swain telemetry enable --endpoint URL")
        return 1
    
    event_dir = Path.home() / ".swain" / "telemetry" / "events"
    
    # Get summaries to export
    if start_date and end_date:
        dates = get_date_range(start_date, end_date)
    else:
        # Get unexported summaries
        last_export = config.get("last_export")
        dates = get_unexported_dates(last_export)
    
    summaries = []
    for date in dates:
        summary_file = event_dir / f"{date}-summary.json"
        if summary_file.exists():
            summaries.append(json.loads(summary_file.read_text()))
    
    if not summaries:
        print("No summaries to export.")
        return 0
    
    if dry_run:
        print("Would export:")
        print(json.dumps({
            "summaries": summaries,
            "exported_at": datetime.now().isoformat(),
            "swain_version": "0.27.1"
        }, indent=2))
        return 0
    
    # Prompt for first export to new endpoint
    if not config.get("export_confirmed"):
        response = input(f"Export to {endpoint}? [y/N] ")
        if response.lower() != 'y':
            print("Export cancelled.")
            return 0
        config["export_confirmed"] = True
        config_path.write_text(json.dumps(config, indent=2))
    
    # POST to endpoint
    payload = {
        "summaries": summaries,
        "exported_at": datetime.now().isoformat(),
        "swain_version": "0.27.1"
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"Exported {len(summaries)} summaries successfully.")
            # Update last export
            config["last_export"] = datetime.now().isoformat()
            config_path.write_text(json.dumps(config, indent=2))
        else:
            print(f"Export failed: {response.status_code} {response.text}")
            
    except requests.Timeout:
        print("Export timed out (30s). Will retry on next attempt.")
    except requests.ConnectionError as e:
        print(f"Export failed: {e}")
    
    # Log export attempt
    log_export_attempt(len(summaries), response.status_code if 'response' in locals() else None)
```

## Dependencies
- EPIC-057 (parent epic)
- SPEC-246 (aggregator)
- SPEC-244 (config management)

## Test Plan
- [ ] Export command works
- [ ] Endpoint validation
- [ ] Dry-run mode works
- [ ] First-export confirmation works
- [ ] Success response handled correctly
- [ ] Error responses handled correctly
- [ ] Timeout handled correctly
- [ ] Export log maintained
- [ ] No identifiers in exported data
- [ ] OTLP-compatible format

## Linked Design Intent
From DESIGN-015:
- **Goal**: Operator-controlled export, local-first
- **Principle**: Auditable, easy opt-out
- **Deferred**: Backend endpoint (operator provides)
