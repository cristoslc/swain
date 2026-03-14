---
id: swa-mnln
status: closed
deps: [swa-xpe1]
links: []
created: 2026-03-13T23:26:49Z
type: task
priority: 1
assignee: cristos
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement OSC 8 link helpers

Implement link formatting utilities in a new links.py module. art_link(aid, file, repo) returns OSC 8 hyperlink when stdout isatty, plain text otherwise. Must match bash escape sequences exactly.


## Notes

**2026-03-14T05:01:16Z**

Completed: links.py created with art_link, file_link, is_tty. Tests passing.
