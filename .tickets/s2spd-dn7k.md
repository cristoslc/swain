---
id: s2spd-dn7k
status: closed
deps: [s2spd-cgkr]
links: []
created: 2026-04-13T13:30:51Z
type: task
priority: 2
assignee: cristos
parent: s2spd-5lo8
tags: [spec:SPEC-297]
---
# Implement SWAIN_PURPOSE → bookmark + JSON field in greeting

In skills/swain-session/scripts/swain-session-greeting.sh: if $SWAIN_PURPOSE is set and no existing bookmark, call swain-bookmark.sh with it, then re-read. Add 'purpose' field to the JSON output. Make the test from task 1 pass (GREEN).


## Notes

**2026-04-13T14:21:29Z**

GREEN: 9/9 tests pass. Added PURPOSE extraction from SWAIN_PURPOSE env var in swain-session-greeting.sh; bookmark written via swain-bookmark.sh only when no existing bookmark (preserves operator context); surfaced as 'purpose' field in JSON and 'Purpose:' line in human-readable output.
