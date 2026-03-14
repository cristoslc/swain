---
id: swa-zd19
status: closed
deps: []
links: []
created: 2026-03-14T06:04:17Z
type: task
priority: 2
assignee: Cristos L-C
tags: [spec:SPEC-037]
---
# SPEC-037: verify specgraph ready standing-track fix

Verify specgraph.sh and specgraph.py do_ready already correctly exclude standing-track artifacts. Tags for tracking.


## Notes

**2026-03-14T06:04:17Z**

Verified: both specgraph.sh (line 306, is_resolved def) and specgraph.py (resolved.py module with _STANDING_TYPES) already exclude ADR/PERSONA/VISION/JOURNEY/RUNBOOK/DESIGN at Active status from ready output. Running specgraph.sh ready and specgraph.py ready shows no standing-track artifacts. Fix was already in place.
