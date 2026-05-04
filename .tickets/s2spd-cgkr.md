---
id: s2spd-cgkr
status: closed
deps: []
links: []
created: 2026-04-13T13:30:51Z
type: task
priority: 2
assignee: cristos
parent: s2spd-5lo8
tags: [spec:SPEC-297]
---
# Write failing test: greeting reads SWAIN_PURPOSE and writes bookmark

Add test (tests/test_session_purpose.sh or extend test_pre_runtime.sh) that: 1) sets SWAIN_PURPOSE=<text> in a tmpdir repo with no existing bookmark, 2) runs swain-session-greeting.sh, 3) asserts session.json bookmark == <text>, 4) asserts greeting JSON 'purpose' field == <text>. Test must FAIL against current code (RED).


## Notes

**2026-04-13T14:19:14Z**

RED confirmed: 3 failing assertions in tests/test_session_purpose.sh — bookmark.note not written, purpose field missing from JSON, Purpose line missing from human output. 6 guard tests pass.
